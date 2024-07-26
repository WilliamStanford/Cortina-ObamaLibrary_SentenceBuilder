from flask import Flask, render_template, request, session, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key

# Options for each part of the sentence
options = {
    'w': ['mother', 'father', 'sister', 'brother'],
    'x': ['kind', 'strict', 'funny', 'smart'],
    'y': ['shaped', 'influenced', 'changed', 'defined'],
    'z': ['future', 'perspective', 'career', 'values']
}

step_names = {
    'w': 'Step 1',
    'x': 'Step 2',
    'y': 'Step 3',
    'z': 'Step 4'
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
    sentence = "My "
    if 'w' in session:
        sentence += f"{session['w']} is a "
    if 'x' in session:
        sentence += f"{session['x']} and that "
    if 'y' in session:
        sentence += f"{session['y']} my "
    if 'z' in session:
        sentence += f"{session['z']}"
    return sentence

if __name__ == '__main__':
    app.run(debug=True)
