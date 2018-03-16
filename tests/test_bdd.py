import pytest

from sismic.interpreter import Event
from sismic.bdd.cli import execute_cli
from sismic.bdd import steps


def test_elevator():
    d = lambda f: 'docs/examples/elevator/' + f

    assert 0 == execute_cli(
        statechart=d('elevator_contract.yaml'),
        features=[d('elevator.feature')],
        steps=[],
        properties=[],
        debug_on_error=False,
        parameters= []
    )


def test_microwave():
    d = lambda f: 'docs/examples/microwave/' + f

    assert 0 == execute_cli(
        statechart=d('microwave.yaml'),
        features=[d('heating.feature')],
        steps=[],
        properties=[],
        debug_on_error=False,
        parameters=[]
    )


def test_microwave_with_properties():
    d = lambda f: 'docs/examples/microwave/' + f

    assert 0 == execute_cli(
        statechart=d('microwave.yaml'),
        features=[d('heating.feature')],
        steps=[],
        properties=[d('heating_off_property.yaml'), d('heating_on_property.yaml'), d('heating_property.yaml')],
        debug_on_error=False,
        parameters=[]
    )


def test_microwave_with_steps():
    d = lambda f: 'docs/examples/microwave/' + f

    assert 0 == execute_cli(
        statechart=d('microwave.yaml'),
        features=[d('heating_human.feature')],
        steps=[d('heating_steps.py')],
        properties=[],
        debug_on_error=False,
        parameters=[]
    )


def test_microwave_with_steps_and_properties():
    d = lambda f: 'docs/examples/microwave/' + f

    assert 0 == execute_cli(
        statechart=d('microwave.yaml'),
        features=[d('heating_human.feature')],
        steps=[d('heating_steps.py')],
        properties=[d('heating_off_property.yaml'), d('heating_on_property.yaml'), d('heating_property.yaml')],
        debug_on_error=False,
        parameters=[]
    )


class TestSteps:
    @pytest.fixture
    def context(self, mocker):
        context = mocker.MagicMock(name='context')

        context.interpreter = mocker.MagicMock(name='interpreter')
        context.interpreter.queue = mocker.MagicMock(name='queue')
        context.interpreter.context = {'x': 1}
        context.execute_steps = mocker.MagicMock(name='execute_steps')
        context.monitored_trace = []

        return context

    @pytest.fixture
    def trace(self, mocker):
        macrostep = mocker.MagicMock()
        macrostep.entered_states = ['a', 'b', 'c']
        macrostep.exited_states = ['x', 'y', 'z']
        macrostep.sent_events = [Event('e1'), Event('e2'), Event('e3')]

        return [macrostep]

    def test_do_nothing(self, context):
        steps.do_nothing(context)
        context.interpreter.queue.assert_not_called()

    def test_repeat_step(self, context):
        steps.repeat_step(context, 'blabla', 3)
        assert context.execute_steps.call_count == 3
        context.execute_steps.assert_called_with('Given blabla')

    def test_send_event(self, context):
        steps.send_event(context, 'event_name')
        context.interpreter.queue.assert_called_with(Event('event_name'))

    def test_send_event_with_parameter(self, context):
        steps.send_event(context, 'event_name', 'x', '1')
        context.interpreter.queue.assert_called_with(Event('event_name', x=1))

    def test_wait(self, context):
        context.interpreter.time = 0
        steps.wait(context, 3)
        assert context.interpreter.time == 3

        steps.wait(context, 6)
        assert context.interpreter.time == 9

    def test_state_is_entered(self, context, trace):
        context.monitored_trace = []
        with pytest.raises(AssertionError):
            steps.state_is_entered(context, 'state')

        context.monitored_trace = trace
        steps.state_is_entered(context, 'a')
        steps.state_is_entered(context, 'b')
        steps.state_is_entered(context, 'c')
        with pytest.raises(AssertionError):
            steps.state_is_entered(context, 'state')

    def test_state_is_not_entered(self, context, trace):
        context.monitored_trace = []
        steps.state_is_not_entered(context, 'state')

        context.monitored_trace = trace
        with pytest.raises(AssertionError):
            steps.state_is_not_entered(context, 'a')
        steps.state_is_not_entered(context, 'state')

    def test_state_is_exited(self, context, trace):
        context.monitored_trace = []
        with pytest.raises(AssertionError):
            steps.state_is_exited(context, 'state')

        context.monitored_trace = trace
        steps.state_is_exited(context, 'x')
        steps.state_is_exited(context, 'y')
        steps.state_is_exited(context, 'z')
        with pytest.raises(AssertionError):
            steps.state_is_entered(context, 'state')

    def test_state_is_not_exited(self, context, trace):
        context.monitored_trace = []
        steps.state_is_not_exited(context, 'state')

        context.monitored_trace = trace
        with pytest.raises(AssertionError):
            steps.state_is_not_exited(context, 'x')
        steps.state_is_not_exited(context, 'state')

    def test_state_is_active(self, context):
        context.interpreter.configuration = []
        with pytest.raises(AssertionError):
            steps.state_is_active(context, 'state')

        context.interpreter.configuration = ['a', 'b', 'c']
        steps.state_is_active(context, 'a')
        steps.state_is_active(context, 'b')
        steps.state_is_active(context, 'c')
        with pytest.raises(AssertionError):
            steps.state_is_active(context, 'state')

    def test_state_is_not_active(self, context):
        context.interpreter.configuration = []

        steps.state_is_not_active(context, 'state')

        context.interpreter.configuration = ['a', 'b', 'c']
        with pytest.raises(AssertionError):
            steps.state_is_not_active(context, 'a')

        steps.state_is_not_active(context, 'state')

    def test_event_is_fired(self, context, trace):
        context.monitored_trace = []
        with pytest.raises(AssertionError):
            steps.event_is_fired(context, 'event')

        context.monitored_trace = trace
        steps.event_is_fired(context, 'e1')
        steps.event_is_fired(context, 'e2')
        steps.event_is_fired(context, 'e3')

        with pytest.raises(AssertionError):
            steps.event_is_fired(context, 'event')

    def test_event_is_fired_with_parameter(self, context, trace):
        context.monitored_trace = trace
        context.monitored_trace[0].sent_events = [Event('e1', x=1)]

        steps.event_is_fired(context, 'e1')

        with pytest.raises(AssertionError):
            steps.event_is_fired(context, 'event')

        with pytest.raises(AssertionError):
            steps.event_is_fired(context, 'e1', 'x', '2')

        steps.event_is_fired(context, 'e1', 'x', '1')

    def test_event_is_not_fired(self, context, trace):
        context.monitored_trace = []

        steps.event_is_not_fired(context, 'event')

        context.monitored_trace = trace
        with pytest.raises(AssertionError):
            steps.event_is_not_fired(context, 'e1')

        steps.event_is_not_fired(context, 'event')

    def test_no_event_is_fired(self, context, trace):
        context.monitored_trace = []
        steps.no_event_is_fired(context)

        context.monitored_trace = trace
        with pytest.raises(AssertionError):
            steps.no_event_is_fired(context)

    def test_variable_equals(self, context):
        steps.variable_equals(context, 'x', '1')

        with pytest.raises(AssertionError):
            steps.variable_equals(context, 'y', '1')

        with pytest.raises(AssertionError):
            steps.variable_equals(context, 'x', '2')

    def test_variable_does_not_equal(self, context):
        steps.variable_does_not_equal(context, 'x', '2')

        with pytest.raises(AssertionError):
            steps.variable_does_not_equal(context, 'x', '1')

        with pytest.raises(AssertionError):
            steps.variable_does_not_equal(context, 'y', '1')

    def test_final_configuration(self, context):
        context.interpreter.final = True
        steps.final_configuration(context)

        context.interpreter.final = False
        with pytest.raises(AssertionError):
            steps.final_configuration(context)

    def test_not_final_configuration(self, context):
        context.interpreter.final = False
        steps.not_final_configuration(context)

        context.interpreter.final = True
        with pytest.raises(AssertionError):
            steps.not_final_configuration(context)