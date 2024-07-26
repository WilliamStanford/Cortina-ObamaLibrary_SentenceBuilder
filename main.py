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
    'z': 'Step 4',
}

sentence_structure = {
    'wxyz': { 
        "1": f"{session['w']} is a "
        "2": f"{session['x']} and that ",
        "3": f"{session['y']} my "
        "4": f"{session['z']}"
    }
    
             

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'step' not in session:
        session['step'] = '1'

    if request.method == 'POST':
        choice = request.form.get('choice')
        current_step = session['step']

        session[current_step] = choice

        if current_step == '1':
            session['step'] = '2'
        elif current_step == '2':
            session['step'] = '3'
        elif current_step == '3':
            session['step'] = '4'
        elif current_step == '4':
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
    if '1' in session:
        sentence += sentence_structure['wxyz']['1']
    if '2' in session:
        sentence += sentence_structure['wxyz']['2']
    if '3' in session:
        sentence += sentence_structure['wxyz']['3']
    if '4' in session:
        sentence += sentence_structure['wxyz']['4']
    return sentence

if __name__ == '__main__':
    app.run(debug=True)
