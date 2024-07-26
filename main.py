from flask import Flask, render_template, request, session, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key

# Options for each part of the sentence
options = {
    'w': ['My mother is', 'My father is', 'My aunt is', 'My sister is'],
    'x': ['a leader', 'a visionary', 'a caregiver', 'a mentor'],
    'y': ['and that influenced my', 'and that formed my', 'and that defined my', 'and that nurtured my'],
    'z': ['resilience', 'approach to challenges', 'courage', 'core values']
}

step_names = {
    'w': 'Step 1', 
    'x': 'Step 2',
    'y': 'Step 3',
    'z': 'Step 4',
}


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'step' not in session:
        session['step'] = 'w'

    if request.method == 'POST':
        choice = request.form.get('choice')
        current_step = session['step']

        session[current_step] = choice

        if current_step == 'w':
            session['step'] = 'x'
        elif current_step == 'x':
            session['step'] = 'y'
        elif current_step == 'y':
            session['step'] = 'z'
        elif current_step == 'z':
            session['step'] = 'complete'

        return redirect(url_for('index'))

    current_step = session['step']
    step_name = step_names.get(current_step, 'Complete')
    return render_template('form.html', 
                           options=options.get(current_step, []),
                           current_step=current_step,
                           step_name=step_name,
                           sentence=build_sentence())

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

def build_sentence():
    sentence = ""
    if 'w' in session:
        sentence += session['w'] + ' '
    if 'x' in session:
        sentence += session['x'] + ' '
    if 'y' in session:
        sentence += session['y'] + ' '
    if 'z' in session:
        sentence += session['z'] + ' '
    return sentence

if __name__ == '__main__':
    app.run(debug=True)
