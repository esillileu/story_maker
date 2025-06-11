from flask import Flask, render_template, request, redirect, url_for
from core.db import get_latest_state, get_state, list_timelines
from core.nodes import present_situation, decide_speaker, npc_flow, user_flow, judge_event_end, wrapup
from core.logconfig import config_logging

app = Flask(__name__)
config_logging()

graph_state = get_latest_state()
history = []

def advance_until_user():
    global graph_state, history
    while True:
        if not graph_state.situation:
            graph_state = present_situation(graph_state)
            history.append(graph_state.situation)
        graph_state = decide_speaker(graph_state)
        if graph_state.turn == 'user':
            break
        graph_state = npc_flow(graph_state)
        history.append(graph_state.output)
        graph_state = judge_event_end(graph_state)
        if graph_state.event_complete:
            graph_state = wrapup(graph_state)

@app.route('/')
def index():
    timelines = list_timelines()
    input_disabled = graph_state.turn != 'user'
    return render_template('index.html', timelines=timelines, history=history, input_disabled=input_disabled)

@app.post('/send')
def send_message():
    global graph_state, history
    message = request.form.get('message', '')
    graph_state = graph_state.model_copy(update={'pending_user_input': message})
    history.append(message)
    graph_state = user_flow(graph_state)
    graph_state = judge_event_end(graph_state)
    if graph_state.event_complete:
        graph_state = wrapup(graph_state)
    advance_until_user()
    return redirect(url_for('index'))

@app.get('/timeline/<tl>')
def select_timeline(tl):
    global graph_state, history
    graph_state = get_state(tl)
    history.clear()
    advance_until_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    advance_until_user()
    app.run(debug=True)
