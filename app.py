from flask import Flask, render_template, redirect, url_for, request, flash
import json
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Set a secret key for flash messages

# Helper functions to load and save recipe data from/to a JSON file
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

def load_recipes_data():
    data_file_path = os.path.join(os.path.dirname(__file__), 'data', 'recipes_data.json')
    if os.path.exists(data_file_path):
        with open(data_file_path, 'r') as file:
            recipes = json.load(file)
        print("Loaded recipes:", recipes)  # Add this line for debugging
    else:
        recipes = []
    return recipes

def save_recipes_data(recipes):
    data_file_path = os.path.join(os.path.dirname(__file__), 'data', 'recipes_data.json')
    with open(data_file_path, 'w') as file:
        json.dump(recipes, file, indent=4)

@app.route('/')
def index():
    recipes = load_recipes_data()
    return render_template('index.html', recipes=recipes)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/recipes')
def view_recipes():
    recipes = load_recipes_data()
    return render_template('Recipes.html', recipes=recipes)

def calculate_recipe_id_counter():
    # Load existing recipes
    recipes = load_recipes_data()

    # Calculate the next recipe ID based on the number of existing recipes
    if recipes:
        max_recipe = max(recipes, key=lambda x: x.get('id'))
        return max_recipe['id'] + 1
    else:
        return 1  # Start with 1 if there are no existing recipes

# Initialize the recipe_id_counter
recipe_id_counter = calculate_recipe_id_counter()

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/form', methods=['GET', 'POST'])
def add_recipe():
    global recipe_id_counter  # Declare the use of the global variable
    if request.method == 'POST':
        name = request.form.get('name')
        about = request.form.get('about')
        time = request.form.get('time')
        category = request.form.get('category')

        ingredients = [request.form.get(f'ing{i}') for i in range(1, 9) if request.form.get(f'ing{i}')]

        steps = [request.form.get(f'step{i}') for i in range(1, 9) if request.form.get(f'step{i}')]

        image_file = request.files['image_file']

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_recipe = {
            'id': recipe_id_counter,
            'name': name,
            'about': about,
            'time':time,
            'category': category,
            'ingredients': ingredients,
            'steps': steps,
            'image_path': f'uploads/{filename}'
        }
        recipe_id_counter += 1

        recipes = load_recipes_data()

        # Append the new recipe to the existing recipes
        recipes.append(new_recipe)

        # Save the updated list of recipes
        save_recipes_data(recipes)

        flash('Recipe added successfully!', 'success')
        return redirect(url_for('view_recipes'))

    return render_template('add_recipes.html')

@app.route('/recipes_details/<int:recipe_id>')
def recipes_details(recipe_id):
    # Load your recipe data and retrieve the recipe with the specified UUID
    recipes = load_recipes_data()
    selected_recipe = None
    for recipe in recipes:
        if recipe.get('id') == recipe_id:
            selected_recipe = recipe
            break

    if selected_recipe:
        return render_template('recipes_details.html', recipe=selected_recipe)
    else:
        # Handle the case where the recipe with the specified UUID is not found
        flash('Recipe not found', 'error')
        return redirect(url_for('view_recipes'))



@app.route('/search_results')
def search_results():
    query = request.args.get('query')
    # Filter your recipe data based on the search query
    # Here, you can search through recipe names, categories, or any other relevant fields
    filtered_recipes = [recipe for recipe in load_recipes_data() if query.lower() in recipe['name'].lower()]
    return render_template('search_results.html', query=query, recipes=filtered_recipes)



if __name__ == '__main__':
    app.run(debug=True)
