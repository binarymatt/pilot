from flask import Flask, render_template, flash, url_for, redirect, request
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver


app = Flask(__name__)
app.config['FILTER_NAMES'] = []
app.config.from_pyfile('application.cfg', silent=True)
Driver = get_driver(Provider.RACKSPACE)
conn = Driver(app.config['RACKSPACE_USER'], app.config['RACKSPACE_KEY'])

def filter_nodes(node):
    return node.name not in app.config['FILTER_NAMES']

@app.route("/")
def hello():
    nodes = conn.list_nodes()
    nodes = filter(filter_nodes, nodes)
    return render_template('node_list.html', nodes=nodes)

@app.route('/destroy/<int:node_id>/', methods=["GET","POST"])
def destroy(node_id):
    node = conn.ex_get_node_details(node_id)
    if request.method == "POST":
        node.destroy()
        flash("deleted server",category="warning")
        return redirect(url_for('hello'))
    return render_template('delete_confirmation.html',node=node)

@app.route('/rename/<int:node_id>/', methods=["GET","POST"])
def rename(node_id):
    node = conn.ex_get_node_details(node_id)
    if request.method == "POST":
        name = request.form['name']
        conn.ex_set_server_name(node,name)
        flash("renamed server",category="warning")
        return redirect(url_for('hello'))
    return render_template('rename.html',node=node)

@app.route('/change_pass/<int:node_id>/', methods=["GET","POST"])
def change_password(node_id):
    node = conn.ex_get_node_details(node_id)
    if request.method == "POST":
        password = request.form['password']
        conn.ex_set_password(node, password)
        flash('password changed', category='success')
        return redirect(url_for('hello'))
    return render_template('change_password.html',node=node)

@app.route('/images/')
def list_images():
    images = conn.list_images()
    images.sort(key=lambda item: int(item.id))
    return render_template('list_images.html',images=images)

@app.route('/flavors/')
def list_flavors():
    flavors = conn.list_sizes()
    return render_template('list_flavors.html', sizes=flavors)


app.secret_key = '\xc5\x1d\x86M\xf6\xd3\xa9<\xda\x17p>Eo\xb9|\x7f\xe3\x81\xce\x0b\xc9\xf7\xb6'
if __name__ == "__main__":
    app.run(debug=True)
