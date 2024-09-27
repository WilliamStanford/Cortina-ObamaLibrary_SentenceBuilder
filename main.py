from flask import Flask, render_template, request, session, redirect, url_for, flash
from pymilvus import model
from pymilvus import MilvusClient
import random
import re
import json 
import argparse


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key

with open('options.json') as f:
    options = json.load(f)

vector_sim = True

def generate_embeddings():
    sentence_structures = options['sentence_structures']

    embedding_fn = model.DefaultEmbeddingFunction()
    client = MilvusClient("sentence_summaries.db")
    data = [
        {
            "id": i, 
            "vector": embedding_fn.encode_documents(sentence_structures[i]['summary_word'])[0],  # Embeds summary word into vector
            "text": sentence_structures[i]['summary_word'],
            "template": sentence_structures[i]['template'],
            "x_type": sentence_structures[i]['x_type']
        } for i in range(len(sentence_structures))
    ] 
    


    if client.has_collection(collection_name="summary_word"):
        client.drop_collection(collection_name="summary_word")
    client.create_collection(
        collection_name="summary_word",
        dimension=768,  # The vectors we will use in this demo has 768 dimensions
    )
    client.insert(collection_name="summary_word", data=data)



def choose_sentence_structure(family_words):

    if vector_sim:
        family_words = [", ".join(family_words)]
        embedding_fn = model.DefaultEmbeddingFunction()
        client = MilvusClient("sentence_summaries.db")
        query_vectors = embedding_fn.encode_queries(family_words)

        res = client.search(
            collection_name="summary_word",  # target collection
            data=query_vectors,  # query vectors
            limit=3,  # number of returned entities
            output_fields=["text", "template", "x_type"],  # specifies fields to be returned
        )

        dumped_data = json.dumps(res)
        parsed_data = json.loads(dumped_data)[0]
        chosen_data = random.choice(parsed_data) # Adds some randomness rather than always returning the most similar sentence
        sentence_structure = chosen_data['entity']
    else:
        sentence_structure = random.choice(options['sentence_structures'])


    return sentence_structure


def get_structure_order(structure):
    return re.findall(r'\{(\w)\}', structure['template'])


@app.route('/', methods=['GET'])
def index():

    if vector_sim:
        print('GENERATING EMBEDDINGS')
        generate_embeddings()
        print('Finished generating embeddings')

    return render_template('start.html', word_options=options["self_words"])


# For choosing words that describe self
@app.route('/choose_words', methods=['POST'])
def choose_words():
    words = request.form.get('words', '').split(',')
    words = [word.strip() for word in words if word.strip()]
    if len(words) > 4:
        return redirect(url_for('index'))
    session['personal_words'] = words
    return redirect(url_for('choose_shaper'))


@app.route('/choose_shaper', methods=['GET', 'POST'])
def choose_shaper():
    if request.method == 'POST':
        shaper = request.form.get('shaper')
        if shaper:
            session['shaper'] = shaper
            return redirect(url_for('choose_family_words'))
        return redirect(url_for('choose_shaper'))
    return render_template('choose_shaper.html', shaper_options=options['shapers'])


@app.route('/choose_family_words', methods=['GET', 'POST'])
def choose_family_words():
    if request.method == 'POST':
        family_words_selected = request.form.getlist('family_words')
        if 0 < len(family_words_selected) <= 4:
            # Choose sentence structure here, based on family words
            session['structure'] = choose_sentence_structure(family_words_selected)
            session['order'] = get_structure_order(session['structure'])
            session['current_index'] = 0  # Start from the first variable (usually 'x')
            return redirect(url_for('start'))
        else:
            flash('Please select between 1 and 4 family words.', 'error')
            return redirect(url_for('choose_family_words'))
    
    # This part handles the GET request
    return render_template('choose_family_words.html', family_words=options['family_words'])

@app.route('/start', methods=['GET', 'POST'])
def start():
    if 'structure' not in session:
        return redirect(url_for('choose_relative'))

    if request.method == 'POST':
        choice = request.form.get('choice')
        if not choice:
            return redirect(url_for('start'))
        
        current_step = session['order'][session['current_index']]
        
        if current_step == 'x':
            session['x'] = choice
            session['x_no_article'] = choice.split(' ', 1)[1] if choice.startswith(('a ', 'an ')) else choice
        else:
            session[current_step] = choice
        
        session['current_index'] += 1
        if session['current_index'] >= len(session['order']):
            session['current_index'] = 'complete'
        
        return redirect(url_for('start'))
    
    if session.get('current_index') == 'complete':
        current_step = 'complete'
    else:
        current_step = session['order'][session['current_index']]
    
    step_name = f"Step {session['current_index'] + 1}" if current_step != 'complete' else 'Complete'
    
    x_options = options['x'] if session['structure']['x_type'] == 'x' else [x.split(' ', 1)[1] if x.startswith(('a ', 'an ')) else x for x in options['x']]
    
    return render_template('form.html', 
                           options=x_options if current_step == 'x' else options.get(current_step, []),
                           current_step=current_step,
                           step_name=step_name,
                           sentence=build_sentence())


def build_sentence():
    if session.get('current_index') == 'complete':
        x_key = 'x' if session['structure']['x_type'] == 'x' else 'x_no_article'
        return session['structure']['template'].format(shaper=session.get('shaper', '_____'),
                                                       x=session.get(x_key, '_____'),
                                                       y=session.get('y', '_____'),
                                                       z=session.get('z', '_____'))
    else:
        partial_structure = session['structure']['template']
        for part in session['order'][session['current_index']:]:
            partial_structure = partial_structure.split('{' + part + '}')[0]
        return partial_structure.format(shaper=session.get('shaper', '_____'),
                                        **{k: session.get(k, '_____') for k in 'xyz'})


@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':

    app.run(debug=True)