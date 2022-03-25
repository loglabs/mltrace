from mltrace import Component


class BoyuanComponent(Component):
    def __init__(
        self,
        name = "",
        owner = "",
        description = "",
        beforeTests = [],
        afterTests = [],
        tags = [],
    ):
        super().__init__(name, owner, description, beforeTests, afterTests, tags)

    # overwrite afterRun
    def afterRun(self):
        histories = self._history.get_runs_by_index(0,1)
        history_length = len(self._history)


new_component = BoyuanComponent("test", "boyuan_component")


@new_component.run(auto_log=True)
def test_boyuan_component(num):
    num += 2
    return num ** 2


test_boyuan_component(5)
