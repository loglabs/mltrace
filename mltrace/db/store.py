from datetime import datetime
from mltrace.db.utils import (
    _create_engine_wrapper,
    _initialize_db_tables,
    _drop_everything,
    _map_extension_to_enum,
)
from mltrace.db import (
    Component,
    ComponentRun,
    IOPointer,
    PointerTypeEnum,
    Tag,
    component_run_output_association,
)
from mltrace.db.models import component_run_output_association
from sqlalchemy import func, and_
from sqlalchemy.orm import sessionmaker, joinedload

import logging
import typing


class Store(object):
    """Helper methods to interact with the db."""

    def __init__(self, uri: str, delete_first: bool = False):
        """
        Creates the postgres database for the store. Raises exception if uri
        isn't prefixed with postgresql://.

        Args:
            uri (str): URI string to connect to the SQLAlchemy database.
            delete_first (bool): Whether all the tables in the db should be deleted.
        """
        if uri.lower().strip() == "test":
            uri = "sqlite:///:memory:"

        elif not uri.startswith("postgresql://"):
            raise RuntimeError("Database URI must be prefixed with `postgresql://`")

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
        self, name: str, description: str, owner: str, tags: typing.List[str] = []
    ):
        """Creates a component entity in the database if it does not already exist."""
        res = self.get_component(name)

        if res:
            logging.info(f'Component with name "{name}" already exists.')
            return

        # Add to the DB if it is not already there
        logging.info(
            f'Creating new Component with name "{name}", description "{description}", owner "{owner}", and tags "{tags}".'
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
            self.session.query(ComponentRun).filter(ComponentRun.id == id).first()
        )

        return component_run

    def add_tags_to_component(self, component_name: str, tags: typing.List[str]):
        """Retreives existing component and adds tags."""
        component = self.get_component(component_name)

        if not component:
            raise RuntimeError(f'Component with name "{component_name}" not found.')

        tag_objects = list(set([self.get_tag(t) for t in tags]))
        component.add_tags(tag_objects)
        self.session.commit()

    def initialize_empty_component_run(self, component_name: str) -> ComponentRun:
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
        self, names: typing.List[str], pointer_type: PointerTypeEnum = None
    ) -> typing.List[IOPointer]:
        """Creates io pointers around the specified path names. Retrieves existing io pointer if exists in DB, otherwise creates a new one with inferred pointer type."""
        res = self.session.query(IOPointer).filter(IOPointer.name.in_(names)).all()
        res_names = set([r.name for r in res])
        need_to_add = set(names) - res_names

        if len(need_to_add) != 0:
            # Create new IOPointers
            if pointer_type == None:
                pointer_type = _map_extension_to_enum(next(iter(need_to_add)))
            iops = [
                IOPointer(name=name, pointer_type=pointer_type) for name in need_to_add
            ]
            self.session.add_all(iops)
            self.session.commit()
            return res + iops

        return res

    def get_io_pointer(
        self, name: str, pointer_type: PointerTypeEnum = None, create=True
    ) -> IOPointer:
        """Creates an io pointer around the specified path.
        Retrieves existing io pointer if exists in DB,
        otherwise creates a new one if create flag is set."""
        res = self.session.query(IOPointer).filter(IOPointer.name == name).all()

        # Must create new IOPointer
        if len(res) == 0:
            if create == False:
                raise RuntimeError(
                    f"IOPointer with name {name} noes not exist. Set create flag to True if you would like to create it."
                )

            logging.info(f'Creating new IOPointer with name "{name}".')
            if pointer_type == None:
                pointer_type = _map_extension_to_enum(name)

            iop = IOPointer(name=name, pointer_type=pointer_type)
            self.session.add(iop)
            self.session.commit()
            return iop

        # Return existing object
        return res[0]

    def delete_component(self, component: Component):
        self.session.delete(component)
        logging.info(f'Successfully deleted Component with name "{component.name}".')

    def delete_component_run(self, component_run: ComponentRun):
        self.session.delete(component_run)
        logging.info(
            f'Successfully deleted ComponentRun with id "{component_run.id}" and name "{component_run.component_name}".'
        )

    def delete_io_pointer(self, io_pointer: IOPointer):
        self.session.delete(io_pointer)
        logging.info(f'Successfully deleted IOPointer with name "{io_pointer.name}".')

    def commit_component_run(self, component_run: ComponentRun):
        """Commits a fully initialized component run to the DB."""
        status_dict = component_run.check_completeness()
        if not status_dict["success"]:
            raise RuntimeError(status_dict["msg"])

        if status_dict["msg"]:
            logging.info(status_dict["msg"])

        # Commit to DB
        self.session.add(component_run)
        logging.info(
            f'Committing ComponentRun of type "{component_run.component_name}" to the database.'
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
            .filter(component_run_output_association.c.output_path_name.in_(input_ids))
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
        self, node: ComponentRun, depth: int, node_list: typing.List[ComponentRun]
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

        for dep in sorted(component_run_object.dependencies, key=lambda x: x.id):
            child_res = self._web_trace_helper(dep)
            res["childNodes"].append(child_res)

        return res

    def web_trace(self, output_id: str):
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

        return [self._web_trace_helper(cr) for cr in component_run_objects]

    def trace(self, output_id: str):
        """Prints trace for an output id.
        Returns list of tuples (level, ComponentRun) where level is how
        many hops away the node is from the node that produced the output_id."""
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

    def get_components_with_owner(self, owner: str) -> typing.List[Component]:
        """Returns a list of all the components associated with the specified
        order."""
        components = (
            self.session.query(Component)
            .filter(Component.owner == owner)
            .options(joinedload("tags"))
            .all()
        )

        if len(components) == 0:
            raise RuntimeError(f"Owner {owner} has no components.")

        return components

    def get_components_with_tag(self, tag: str) -> typing.List[Component]:
        """Returns a list of all the components associated with that tag."""
        components = (
            self.session.query(Component)
            .join(Tag, Component.tags)
            .filter(Tag.name == tag)
            .all()
        )

        if len(components) == 0:
            raise RuntimeError(f"Tag {tag} has no components associated.")

        return components

    def get_recent_run_ids(self, limit: int = 50) -> typing.List[str]:
        """Returns a list of recent component run IDs."""
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
