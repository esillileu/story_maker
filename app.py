import time
import threading
from flask import Flask, render_template, request, redirect, url_for, Response
from core.db import (
    get_latest_state,
    get_state,
    list_timelines,
    get_timeline_events,
    get_event_context,
)
from core.nodes import present_situation, decide_speaker, npc_flow, user_flow, judge_event_end, wrapup
from core.logconfig import config_logging

app = Flask(__name__)
config_logging()

graph_state = get_latest_state()
history = []

# Index of history messages already sent to the client

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

def stream_events(start_index: int):
    """Generator yielding new history messages and turn updates."""
    index = start_index
    last_turn = graph_state.turn
    while True:
        if index < len(history):
            msg = history[index]
            index += 1
            yield f"data: {msg}\n\n"
        elif graph_state.turn != last_turn:
            last_turn = graph_state.turn
            yield f"event: turn\ndata: {graph_state.turn}\n\n"
        else:
            time.sleep(0.5)

@app.route('/')
def index():
    timelines = list_timelines()
    input_disabled = graph_state.turn != 'user'
    return render_template('index.html', timelines=timelines, history=history, input_disabled=input_disabled)

@app.get('/stream')
def stream():
    cursor = int(request.args.get('cursor', len(history)))
    return Response(stream_events(cursor), mimetype='text/event-stream')

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
    return ('', 204)

@app.get('/timeline/<tl>')
def select_timeline(tl):
    global graph_state, history
    graph_state = get_state(tl)
    history.clear()
    events = get_timeline_events(tl)
    for eid in events:
        for msg in get_event_context(eid):
            if isinstance(msg, dict):
                history.append(msg.get("content", ""))
            else:
                history.append(str(msg))
    threading.Thread(target=advance_until_user).start()
    return redirect(url_for('index'))

if __name__ == '__main__':
    advance_until_user()
    app.run(debug=True)