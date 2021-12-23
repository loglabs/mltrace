from datetime import datetime, timedelta

from git.index import typ
from sqlalchemy.exc import IntegrityError
from mltrace.db.utils import (
    _create_engine_wrapper,
    _initialize_db_tables,
    _drop_everything,
    _map_extension_to_enum,
    _hash_value,
    _get_data_and_model_args,
    _load,
    _save,
)
from mltrace.db import (
    Component,
    ComponentRun,
    IOPointer,
    PointerTypeEnum,
    Tag,
    Label,
    component_run_output_association,
    deleted_labels,
    output_table,
    feedback_table,
)
from mltrace.db.models import component_run_output_association
from sqlalchemy import func, and_
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.sql.expression import Tuple
from sqlalchemy.dialects.postgresql import insert

import ctypes
import hashlib
import inspect
import logging
import sqlalchemy
import typing


class Store(object):
    """Helper methods to interact with the db."""

    def __init__(self, uri: str, delete_first: bool = False):
        """
        Creates the postgres database for the store. Raises exception if uri
        isn't prefixed with postgresql://.

        Args:
            uri (str): URI string to connect to the SQLAlchemy database.
            delete_first (bool): Whether all the tables in the db should be
                deleted.
        """
        if uri.lower().strip() == "test":
            uri = "sqlite:///:memory:"

        elif not uri.startswith("postgresql://"):
            raise RuntimeError(
                "Database URI must be prefixed with `postgresql://`"
            )

        self.engine = _create_engine_wrapper(uri)

        # TODO(shreyashankar) remove this line
        if delete_first:
            _drop_everything(self.engine)

        # TODO(shreyashankar) check existing tables against expected tables
        _initialize_db_tables(self.engine)

        # Initialize session
        self.Session = sessionmaker(self.engine)
        self.session = self.Session()

    def __del__(self):
        """On destruction, close session."""
        self.session.close()

    def create_component(
        self,
        name: str,
        description: str,
        owner: str,
        tags: typing.List[str] = [],
    ):
        """Creates a component entity in the database if it does
        not already exist."""
        res = self.get_component(name)

        if res:
            logging.info(f'Component with name "{name}" already exists.')
            return

        # Add to the DB if it is not already there
        logging.info(
            f'Creating new Component with name "{name}", description '
            + f'"{description}", owner "{owner}", and tags "{tags}".'
        )
        tags = list(set([self.get_tag(t) for t in tags]))
        component = Component(
            name=name, description=description, owner=owner, tags=tags
        )
        self.session.add(component)
        self.session.commit()

    def get_component(self, name: str) -> Component:
        """Retrieves component if exists."""
        component = (
            self.session.query(Component)
            .outerjoin(Tag, Component.tags)
            .filter(Component.name == name)
            .first()
        )

        return component

    def get_component_run(self, id: str) -> ComponentRun:
        """Retrieves component run if exists."""
        component_run = (
            self.session.query(ComponentRun)
            .filter(ComponentRun.id == id)
            .first()
        )

        return component_run

    def add_tags_to_component(
        self, component_name: str, tags: typing.List[str]
    ):
        """Retreives existing component and adds tags."""
        component = self.get_component(component_name)

        if not component:
            raise RuntimeError(
                f'Component with name "{component_name}" not found.'
            )

        tag_objects = list(set([self.get_tag(t) for t in tags]))
        component.add_tags(tag_objects)
        self.session.commit()

    def unflag_all(self):
        """Unflags all IO Pointers and commits."""
        flagged_iop = (
            self.session.query(IOPointer)
            .filter(IOPointer.flag.is_(True))
            .all()
        )

        for iop in flagged_iop:
            iop.clear_flag()

        self.session.commit()

    def initialize_empty_component_run(
        self, component_name: str
    ) -> ComponentRun:
        """Initializes an empty run for the specified component. Does not
        commit to the database."""
        component_run = ComponentRun(component_name=component_name)
        return component_run

    def get_tag(self, name=str) -> Tag:
        """Creates a tag around the name if it doesn't already exist."""
        res = self.session.query(Tag).filter(Tag.name == name).all()

        # Must create new Tag
        if len(res) == 0:
            logging.info(f'Creating new Tag with name "{name}".')
            tag = Tag(name)
            self.session.add(tag)
            self.session.commit()
            return tag

        # Return existing Tag
        return res[0]

    def get_io_pointers(
        self,
        names: typing.List[str],
        values: typing.List[typing.Any] = None,
        pointer_type: PointerTypeEnum = None,
        labels: typing.List[str] = None,
    ) -> typing.List[IOPointer]:
        """Creates io pointers around the specified path names. Retrieves
        existing io pointer if exists in DB, otherwise creates a new one with
        inferred pointer type."""
        values = (
            [_hash_value(v) for v in values] if values else [b""] * len(names)
        )
        res = (
            self.session.query(IOPointer)
            .filter(
                Tuple(IOPointer.name, IOPointer.value).in_(
                    list(zip(names, values))
                )
            )
            .all()
        )
        # Create label vector
        label_vec = self.get_labels(labels) if labels else None
        if res and labels:
            for iop in res:
                iop.add_labels(label_vec)

        res_names_values = set([(r.name, r.value) for r in res])
        need_to_add = set(zip(names, values)) - res_names_values

        if len(need_to_add) != 0:
            # Create new IOPointers
            if pointer_type is None:
                pointer_type = _map_extension_to_enum(
                    next(iter(need_to_add))[0]
                )
            iops = [
                IOPointer(
                    name=name,
                    value=value,
                    pointer_type=pointer_type,
                )
                for name, value in need_to_add
            ]
            if labels:
                for iop in iops:
                    iop.add_labels(label_vec)
            self.session.add_all(iops)
            self.session.commit()
            return res + iops

        return res

    def get_io_pointer(
        self,
        name: str,
        value: typing.Any = "",
        pointer_type: PointerTypeEnum = None,
        create=True,
        labels: typing.List[str] = None,
    ) -> IOPointer:
        """Creates an io pointer around the specified path.
        Retrieves existing io pointer if exists in DB,
        otherwise creates a new one if create flag is set."""

        hval = _hash_value(value)
        same_name_res = (
            self.session.query(
                component_run_output_association.c.output_path_value
            )
            .filter(
                component_run_output_association.c.output_path_name == name
            )
            .order_by(
                component_run_output_association.c.component_run_id.desc()
            )
            .all()
        )
        same_name_res = [r[0] for r in same_name_res]

        # Create label vector
        label_vec = self.get_labels(labels) if labels else None

        if len(same_name_res) > 0 and bytes(same_name_res[0]) != hval:
            logging.warning(
                f'IOPointer with name "{name}" has a different value '
                + "from the last write."
            )

        res = (
            self.session.query(IOPointer)
            .filter(and_(IOPointer.name == name, IOPointer.value == hval))
            .all()
        )

        # Must create new IOPointer
        if len(res) == 0:
            if create is False:
                raise RuntimeError(
                    f"IOPointer with name {name} noes not exist. Set create"
                    + f" flag to True if you would like to create it."
                )

            logging.info(f'Creating new IOPointer with name "{name}".')
            if pointer_type is None:
                pointer_type = _map_extension_to_enum(name)

            iop = IOPointer(name=name, value=hval, pointer_type=pointer_type)
            if labels:
                iop.add_labels(label_vec)
            self.session.add(iop)
            self.session.commit()
            return iop

        # Return existing object
        # Add labels if they exist
        if labels:
            res[0].add_labels(label_vec)
        return res[0]

    def delete_component(self, component: Component):
        self.session.delete(component)
        logging.info(
            f'Successfully deleted Component with name "{component.name}".'
        )

    def delete_component_run(self, component_run: ComponentRun):
        self.session.delete(component_run)
        logging.info(
            f'Successfully deleted ComponentRun with id "{component_run.id}"'
            + f' and name "{component_run.component_name}".'
        )

    def delete_io_pointer(self, io_pointer: IOPointer):
        self.session.delete(io_pointer)
        logging.info(
            f'Successfully deleted IOPointer with name "{io_pointer.name}".'
        )

    def commit_component_run(
        self,
        component_run: ComponentRun,
        staleness_threshold: int = (60 * 60 * 24 * 30),
    ):
        """Commits a fully initialized component run to the DB."""
        status_dict = component_run.check_completeness()
        if not status_dict["success"]:
            raise RuntimeError(status_dict["msg"])

        if status_dict["msg"]:
            logging.info(status_dict["msg"])

        # Check for staleness
        for dep in component_run.dependencies:
            # First case: there is over a month between component runs
            time_diff = (
                component_run.start_timestamp - dep.start_timestamp
            ).total_seconds()
            if time_diff > staleness_threshold:
                days_diff = int(time_diff // (60 * 60 * 24))
                component_run.add_staleness_message(
                    f"{dep.component_name} (ID {dep.id}) was run {days_diff}"
                    + " days ago."
                )
            # Second case: there is a newer run of the dependency
            fresher_runs = self.get_history(
                dep.component_name,
                limit=None,
                date_lower=dep.start_timestamp,
                date_upper=component_run.start_timestamp,
            )
            fresher_runs = [
                cr for cr in fresher_runs if component_run.id != cr.id
            ]
            if len(fresher_runs) > 1:
                run_or_runs = "run" if len(fresher_runs) - 1 == 1 else "runs"
                component_run.add_staleness_message(
                    f"{dep.component_name} (ID {dep.id}) has "
                    + f"{len(fresher_runs) - 1} fresher {run_or_runs} that "
                    + "began before this component run started."
                )

        # Warn user if there is a staleness message
        if len(component_run.stale) > 0:
            logging.warning(component_run.stale)

        # Dedup labels
        for inp in component_run.inputs:
            inp.dedup_labels()
        for out in component_run.outputs:
            out.dedup_labels()

        # Commit to DB
        self.session.add(component_run)
        logging.info(
            f"Committing ComponentRun {component_run.id} of type "
            + f'"{component_run.component_name}" to the database.'
        )
        self.session.commit()

    def set_dependencies_from_inputs(self, component_run: ComponentRun):
        """Gets IOPointers associated with component_run's inputs, checks
        against any ComponentRun's outputs, and if there are any matches,
        sets the ComponentRun's dependency on the most recent match."""

        input_ids = [inp.name for inp in component_run.inputs]

        if len(input_ids) == 0:
            return

        match_ids = (
            self.session.query(
                func.max(component_run_output_association.c.component_run_id),
            )
            .group_by(component_run_output_association.c.output_path_name)
            .filter(
                component_run_output_association.c.output_path_name.in_(
                    input_ids
                )
            )
            .all()
        )
        match_ids = [m[0] for m in match_ids]

        matches = (
            self.session.query(ComponentRun)
            .filter(ComponentRun.id.in_(match_ids))
            .all()
        )

        # If there are no matches, return
        if len(matches) == 0:
            return

        # Get match with the max timestamp and set upstream
        component_run.set_upstream(matches)

    def _traverse(
        self,
        node: ComponentRun,
        depth: int,
        node_list: typing.List[ComponentRun],
    ):
        # Add node to node_list as the step
        node_list.append((depth, node))

        # Base case
        if len(node.dependencies) == 0:
            return

        # Recurse on neighbors
        for neighbor in node.dependencies:
            self._traverse(neighbor, depth + 1, node_list)

    def _web_trace_helper(self, component_run_object: ComponentRun):
        """Helper function that populates the dictionary of ComponentRuns for
        the web trace. Returns dictionary and counter."""
        res = {}
        res["id"] = f"componentrun_{component_run_object.id}"
        res["label"] = component_run_object.component_name
        res["hasCaret"] = True
        res["isExpanded"] = True
        res["stale"] = component_run_object.stale
        res["childNodes"] = []

        for out in sorted(component_run_object.outputs, key=lambda x: x.name):
            out_dict = {
                "id": f"iopointer_{out.name}",
                "label": out.name,
                "hasCaret": False,
                "parent": res["id"],
            }

            # Settle on icon
            if out.pointer_type == PointerTypeEnum.DATA:
                out_dict["icon"] = "database"
            elif out.pointer_type == PointerTypeEnum.MODEL:
                out_dict["icon"] = "function"
            elif out.pointer_type == PointerTypeEnum.ENDPOINT:
                out_dict["icon"] = "flow-end"

            res["childNodes"].append(out_dict)

        for dep in sorted(
            component_run_object.dependencies, key=lambda x: x.id
        ):
            child_res = self._web_trace_helper(dep)
            res["childNodes"].append(child_res)

        return res

    def web_trace(self, output_id: str, last_only: bool = False):
        """Prints list of ComponentRuns to display in the UI."""
        component_run_objects = (
            self.session.query(ComponentRun)
            .outerjoin(IOPointer, ComponentRun.outputs)
            .order_by(ComponentRun.start_timestamp.desc())
            .filter(IOPointer.name == output_id)
            .all()
        )

        if len(component_run_objects) == 0:
            raise RuntimeError(f"ID {output_id} does not exist.")

        if last_only:
            component_run_objects = [component_run_objects[0]]

        return [self._web_trace_helper(cr) for cr in component_run_objects]

    def trace(self, output_id: str):
        """Prints trace for an output id.
        Returns list of tuples (level, ComponentRun) where level is how
        many hops away the node is from the node that produced the
        output_id."""
        if not isinstance(output_id, str):
            raise RuntimeError("Please specify an output id of string type.")

        component_run_object = (
            self.session.query(ComponentRun)
            .outerjoin(IOPointer, ComponentRun.outputs)
            .order_by(ComponentRun.start_timestamp.desc())
            .filter(IOPointer.name == output_id)
            .first()
        )

        if component_run_object is None:
            raise RuntimeError(f"ID {output_id} does not exist.")

        node_list = []
        self._traverse(component_run_object, 0, node_list)
        return node_list

    def trace_batch(self, output_ids: typing.List[str]):
        pass

    def get_history(
        self,
        component_name: str,
        limit: int = 10,
        date_lower: typing.Union[datetime, str] = datetime.min,
        date_upper: typing.Union[datetime, str] = datetime.max,
    ) -> typing.List[ComponentRun]:
        """Gets lineage for the component, or a history of all its runs."""
        history = (
            self.session.query(ComponentRun)
            .filter(ComponentRun.component_name == component_name)
            .filter(
                and_(
                    ComponentRun.start_timestamp >= date_lower,
                    ComponentRun.start_timestamp <= date_upper,
                )
            )
            .order_by(ComponentRun.start_timestamp.desc())
            .limit(limit)
            .all()
        )

        return history

    def get_components(self, tag: str = "", owner: str = ""):
        """Returns a list of all the components associated with the specified
        owner and/or tags."""
        if tag and owner:
            components = (
                self.session.query(Component)
                .join(Tag, Component.tags)
                .filter(
                    and_(
                        Tag.name == tag,
                        Component.owner == owner,
                    )
                )
                .all()
            )
        elif tag:
            components = (
                self.session.query(Component)
                .join(Tag, Component.tags)
                .filter(Tag.name == tag)
                .all()
            )
        elif owner:
            components = (
                self.session.query(Component)
                .filter(Component.owner == owner)
                .options(joinedload("tags"))
                .all()
            )
        else:
            components = self.session.query(Component).all()

        if len(components) == 0:
            raise RuntimeError(f"Search yielded no components.")

        return components

    def get_recent_run_ids(
        self, limit: int = 50, last_run_id=None
    ) -> typing.List[str]:
        """Returns a list of recent component run IDs."""

        if last_run_id:
            # Get start timestamp of last run id
            ts = (
                self.session.query(ComponentRun)
                .filter(ComponentRun.id == last_run_id)
                .first()
            ).start_timestamp
            if not ts:
                raise RuntimeError(
                    f"Last run ID {last_run_id} does not exist."
                )

            # Return list of runs after ts
            runs = list(
                map(
                    lambda x: int(x[0]),
                    self.session.query(ComponentRun.id)
                    .order_by(ComponentRun.start_timestamp.desc())
                    .filter(
                        and_(
                            ComponentRun.start_timestamp <= ts,
                            ComponentRun.id != last_run_id,
                        )
                    )
                    .limit(limit)
                    .all(),
                )
            )

            return runs

        runs = list(
            map(
                lambda x: int(x[0]),
                self.session.query(ComponentRun.id)
                .order_by(ComponentRun.start_timestamp.desc())
                .limit(limit)
                .all(),
            )
        )

        return runs

    def add_notes_to_component_run(
        self, component_run_id: str, notes: str
    ) -> str:
        """Retreives existing component and adds tags."""
        component_run = self.get_component_run(component_run_id)

        if not component_run:
            raise RuntimeError(
                f'ComponentRun with ID "{component_run_id}" not found.'
            )

        component_run.add_notes(notes)
        self.session.commit()
        return component_run.notes

    def set_io_pointer_flag(self, output_id: str, value: bool):
        """Sets the flag property of an IOPointer."""

        try:
            iop = self.get_io_pointer(output_id, create=False)

            if value:
                iop.set_flag()
            else:
                iop.clear_flag()

            self.session.commit()

            return value

        except RuntimeError:
            raise RuntimeError(
                f"IOPointer with name {output_id} does not exist."
            )

    def review_flagged_outputs(
        self,
    ) -> typing.Tuple[
        typing.List[str], typing.List[typing.Tuple[ComponentRun, int]]
    ]:
        """Finds common ComponentRuns for a group of flagged outputs."""
        # Collate flagged outputs
        flagged_iops = (
            self.session.query(IOPointer)
            .filter(IOPointer.flag.is_(True))
            .all()
        )
        flagged_output_ids = [iop.name for iop in flagged_iops]

        # Perform traces for each output id
        traces = [self.trace(output_id) for output_id in flagged_output_ids]
        traces = [list(set([node for _, node in trace])) for trace in traces]

        # Sort traces by ComponentRun count & id, descending
        trace_nodes_counts = {}
        for trace in traces:
            for node in trace:
                if node not in trace_nodes_counts:
                    trace_nodes_counts[node] = 0
                trace_nodes_counts[node] += 1

        trace_nodes_counts = sorted(
            trace_nodes_counts.items(),
            key=lambda item: (-item[1], -item[0].id),
        )

        # Return a list of the ComponentRuns in the order
        return flagged_output_ids, trace_nodes_counts

    def get_tags(self) -> typing.List[Tag]:
        return self.session.query(Tag).all()

    def get_io_pointers_from_args(
        self, should_filter=True, labels: typing.List[str] = None, **kwargs
    ):
        """Filters kwargs to data and model types,
        then gets corresponding IOPointers."""

        args_filtered = kwargs
        if should_filter:
            args_filtered = _get_data_and_model_args(**kwargs)

        # Create label vector
        label_vec = self.get_labels(labels) if labels else None

        io_pointers = []
        # Hash each arg and see if the corresponding IOPointer exists
        for key, value in args_filtered.items():
            hval = _hash_value(value)
            same_name_res = (
                self.session.query(
                    component_run_output_association.c.output_path_name
                )
                .filter(
                    component_run_output_association.c.output_path_value
                    == hval
                )
                .order_by(
                    component_run_output_association.c.component_run_id.desc()
                )
                .first()
            )

            if same_name_res:
                res = (
                    self.session.query(IOPointer)
                    .filter(
                        and_(
                            IOPointer.name == same_name_res[0],
                            IOPointer.value == hval,
                        )
                    )
                    .all()
                )
                if label_vec:
                    res[0].add_labels(label_vec)
                io_pointers.append(res[0])
                continue

            # See if IOPointer exists but not in output table
            res = (
                self.session.query(IOPointer)
                .filter(
                    IOPointer.value == hval,
                )
                .first()
            )

            if res:
                if label_vec:
                    res.add_labels(label_vec)
                io_pointers.append(res)
                continue

            # Save artifact and create new IOPointer
            pathname = _save(value, var_name=key, from_client=False)
            iop = self.get_io_pointer(pathname, value, labels=labels)
            io_pointers.append(iop)

        return io_pointers

    def get_label(self, label_id: str):
        res = self.session.query(Label).filter(Label.id == label_id).first()

        # If label does not exist, create it
        if not res:
            label = Label(id=label_id)
            self.session.add(label)
            self.session.commit()
            return label

        return res

    def get_labels(self, label_ids: typing.List[str]):

        res = self.session.query(Label).filter(Label.id.in_(label_ids)).all()
        need_to_add = list(set(label_ids) - set([r.id for r in res]))

        if len(need_to_add) > 0:
            labels = [Label(id=label_id) for label_id in need_to_add]
            self.session.add_all(labels)
            self.session.commit()
            return res + labels

        return res

    def assert_not_deleted_labels(
        self,
        io_pointers: typing.List[IOPointer],
        staleness_threshold: int = 0,
    ):
        """Asserts that all labels are not deleted."""
        all_labels = [iop.labels for iop in io_pointers]
        all_labels = [lab.id for labels in all_labels for lab in labels]

        deleted_label_objects = self.session.query(deleted_labels).filter(
            deleted_labels.c.label.in_(all_labels)
        )
        hard_deleted_label_objects = deleted_label_objects.filter(
            deleted_labels.c.deletion_request_time
            < datetime.now() - timedelta(seconds=staleness_threshold)
        ).all()
        soft_deleted_label_objects = deleted_label_objects.filter(
            deleted_labels.c.deletion_request_time
            >= datetime.now() - timedelta(seconds=staleness_threshold)
        ).all()

        if hard_deleted_label_objects:
            raise RuntimeError(
                f"Label(s) {hard_deleted_label_objects}"
                + f" have been deleted."
            )

        if soft_deleted_label_objects:
            for label, time in soft_deleted_label_objects:
                logging.warning(
                    f"You are reading label {label}, which was deleted "
                    + f"{(datetime.now() - time).days} days ago."
                )

    def propagate_labels(
        self, inputs: typing.List[IOPointer], outputs: typing.List[IOPointer]
    ):
        """
        Propagates labels from inputs to outputs.
        """
        all_labels = [inp.labels for inp in inputs]
        all_labels = [lab for labels in all_labels for lab in labels]
        for out in outputs:
            out.add_labels(all_labels)
            self.session.add(out)
        self.session.commit()

    def delete_label(self, label_id: str):
        stmt = insert(deleted_labels).values(
            label=label_id, deletion_request_time=datetime.now()
        )
        stmt = stmt.on_conflict_do_nothing(
            constraint=deleted_labels.primary_key,
        )
        try:
            self.session.execute(stmt)
            self.session.commit()
        except Exception as e:
            if type(e) == sqlalchemy.exc.IntegrityError:
                raise RuntimeError(f"Label {label_id} does not exist.")
            pass

    def delete_labels(self, label_ids: typing.List[str]):
        stmt = insert(deleted_labels).values(
            [
                {"label": label_id, "deletion_request_time": datetime.now()}
                for label_id in label_ids
            ]
        )
        stmt = stmt.on_conflict_do_nothing(
            constraint=deleted_labels.primary_key,
        )
        self.session.execute(stmt)
        self.session.commit()

    def retrieve_deleted_labels(self):
        return self.session.query(deleted_labels).all()

    def retrieve_io_pointers_for_label(self, label_id: str):
        """Retrieves all IOPointers that have the given label."""
        label = self.session.query(Label).filter(Label.id == label_id).first()
        if not label:
            raise RuntimeError(f"Label {label_id} does not exist.")
        return label.io_pointers

    def get_all_labels(self):
        return self.session.query(Label).all()

    def log_output(
        self,
        identifier: str,
        task_name: str,
        val: float,
    ):
        """
        Logs an output value to the output table.
        """

        stmt = insert(output_table).values(
            timestamp=datetime.now(),
            identifier=identifier,
            task_name=task_name,
            value=val,
        )
        self.session.execute(stmt)
        self.session.commit()

    def log_feedback(
        self,
        identifier: str,
        task_name: str,
        val: float,
    ):
        """
        Logs a feedback value to the feedback table.
        """

        stmt = insert(feedback_table).values(
            timestamp=datetime.now(),
            identifier=identifier,
            task_name=task_name,
            value=val,
        )
        self.session.execute(stmt)
        self.session.commit()

    def get_outputs_or_feedback(
        self,
        task_name: str,
        tablename: str = "output_table",
        limit: int = None,
        window_size: int = None,
    ):
        if tablename not in ["output_table", "feedback_table"]:
            raise ValueError(f"Invalid table name {tablename}")

        table = output_table if tablename == "output_table" else feedback_table

        query = self.session.query(
            table.c.timestamp,
            table.c.identifier,
            table.c.value,
        ).filter(table.c.task_name == task_name)

        if limit:
            query = query.order_by(table.c.timestamp.desc()).limit(limit)

        if window_size:
            query = query.filter(
                table.c.timestamp
                >= datetime.now() - timedelta(seconds=window_size)
            )

        return query.all()

    def compute_metric(
        self,
        metric_fn: typing.Callable,
        task_name: str,
        window_size: int = None,
    ):
        """
        Computes a metric over the specified window (in seconds).
        """
        # Check the function is well formed (has y_true, y_pred signature)
        args = inspect.signature(metric_fn)
        if len(args.parameters) < 2:
            raise RuntimeError(
                "The function must take at least two arguments: y_true, y_pred."
            )

        output_join_conditions = [output_table.c.task_name == task_name]
        feedback_join_conditions = [feedback_table.c.task_name == task_name]

        if window_size:
            output_join_conditions.append(
                output_table.c.timestamp
                >= datetime.now() - timedelta(seconds=window_size)
            )
            feedback_join_conditions.append(
                feedback_table.c.timestamp
                >= datetime.now() - timedelta(seconds=window_size)
            )

        join_conditions = output_join_conditions + feedback_join_conditions
        outputs_feedback_joined = (
            self.session.query(feedback_table.c.value, output_table.c.value)
            .join(
                output_table,
                output_table.c.identifier == feedback_table.c.identifier,
            )
            .filter(and_(*join_conditions))
        ).all()

        # Apply the function to each pair of outputs and feedback
        y_true = [float(out[0]) for out in outputs_feedback_joined]
        y_pred = [float(out[1]) for out in outputs_feedback_joined]

        return metric_fn(y_true, y_pred)
