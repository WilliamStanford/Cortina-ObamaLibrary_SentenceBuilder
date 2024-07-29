from flask import Flask, render_template, request, session, redirect, url_for
import os
import random
import re


app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key

# Options for each part of the sentence
#options = {
#    'w': ['My mother is', 'My father is', 'My aunt is', 'My sister is'],
#    'x': ['a leader', 'a visionary', 'a caregiver', 'a mentor'],
#    'y': ['and that influenced my', 'and that formed my', 'and that defined my', 'and that nurtured my'],
#    'z': ['resilience', 'approach to challenges', 'courage', 'core values']
#}

options = {
    'w': ['mother', 'father', 'aunt', 'sister'],
    'x': ['leader', 'visionary', 'caregiver', 'mentor'],
    'y': ['influenced', 'formed', 'defined', 'nurtured'],
    'z': ['resilience', 'approach to challenges', 'courage', 'core values']
}

step_names = {
    'w': 'Step 1',
    'x': 'Step 2',
    'y': 'Step 3',
    'z': 'Step 4'
}

sentence_structures = [
    "My {w} is a {x} who {y} my {z}.",
    "The {x} nature of my {w} {y} my {z} significantly.",
    "In my life, my {x} {w} has greatly {y} my {z}.",
    "I attribute my {z} to my {w}, whose {x} personality {y} me.",
    "My {z} was profoundly {y} by my {w}, a truly {x} individual."
]

def choose_sentence_structure():
    return random.choice(sentence_structures)

def get_structure_order(structure):
    return re.findall(r'\{(\w)\}', structure)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'structure' not in session:
        session['structure'] = choose_sentence_structure()
        session['order'] = get_structure_order(session['structure'])
        session['current_index'] = 0

    if request.method == 'POST':
        choice = request.form.get('choice')
        current_step = session['order'][session['current_index']]
        session[current_step] = choice
        
        session['current_index'] += 1
        if session['current_index'] >= len(session['order']):
            session['current_index'] = 'complete'
        
        return redirect(url_for('index'))
    
    if session.get('current_index') == 'complete':
        current_step = 'complete'
    else:
        current_step = session['order'][session['current_index']]
    
    step_name = f"Step {session['current_index'] + 1}" if current_step != 'complete' else 'Complete'
    
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
    if session.get('current_index') == 'complete':
        return session['structure'].format(**{k: session.get(k, '_____') for k in 'wxyz'})
    else:
        partial_structure = session['structure']
        for part in session['order'][session['current_index']:]:
            partial_structure = partial_structure.split('{' + part + '}')[0]
        return partial_structure.format(**{k: session.get(k, '') for k in 'wxyz'}).strip()

if __name__ == '__main__':
    app.run(debug=True)
