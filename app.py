from typing import BinaryIO, Sized
from flask import Flask, jsonify, make_response, request, send_file
from flask.wrappers import Response
from flask_restful import Api, Resource, abort
import os

from werkzeug.utils import send_file

app = Flask(__name__)
api = Api(app)

output = [
    {
        "pid": "1",
        "title": "Example01",
        "price": 10,
        "img": "https://picsum.photos/id/999/1200/600",
        "isAvailable": True
    },
    {
        "id": "2",
        "title": "Example02",
        "price": 60,
        "img": "https://picsum.photos/id/1070/1200/600",
        "isAvailable": True
    }
]
tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]
# 創建Products 物件並繼承Resource物件
dirpath = os.path.dirname(__file__)


class Products(Resource):
    def get(self):
        return {"products": {"Message": "Get all products..", "output": output}}, 200


@app.route('/')
def index():
    return "this is index"


@app.route('/product')
def product():
    return "this is product"


@app.route('/error')
def error():
    abort(404)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found', "HTTP code": "404"}), 404)


@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_tasks(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    task = list(task)
    print(task, type(task))
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


@app.route('/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201


@app.route('/file/<path:path>', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def render_file(path):
    print('filepath: ', path)
    print('dirpath: ', dirpath)
    newdir = dirpath
    dir = dirpath+'\\'+path
    print('dir: ', dir)
    args_orderBy = request.args.get('orderBy')
    args_orderByDirection = request.args.get('orderByDirection')
    args_filterByName = request.args.get('filterByName')
    print('args_orderBy', args_orderBy)
    print('args_orderByDirection', args_orderByDirection)
    print('args_filterByName', args_filterByName)
    print('----------------------')
    if request.method == 'GET':
        if os.path.isfile(dir):
            print('file exist!')
            f = open(dir, 'rb', buffering=0)
            with open(dir, 'rb', buffering=1)as f:
                print(f.read(10))
            return send_file(dir, environ=request.environ)
        if os.path.isdir(dir):
            print('path exist!')
            subdirectory = os.walk(dir)
            print('subdirectory', subdirectory)
            for i in subdirectory:
                allfilename = i[2]
                tmp_allfilename = []
                print('allfilename', allfilename)
                if args_orderBy == 'lastModified':
                    allfilename = sorted(
                        allfilename, key=lambda x: os.path.getmtime(dir+'\\'+x))
                    print(allfilename, type(allfilename))
                if args_orderBy == 'size':
                    allfilename = sorted(
                        allfilename, key=lambda x: os.path.getsize(dir+'\\'+x))
                    print(allfilename, type(allfilename))
                if args_orderBy == 'fileName':
                    allfilename = sorted(allfilename)
                    print(allfilename, type(allfilename))
                if args_orderByDirection == 'Ascending':
                    print('continue')
                if args_orderByDirection == 'Descending':
                    allfilename.reverse()
                    print('reversed allfilename', allfilename)
                if args_filterByName != None:
                    for each_file in allfilename:
                        print(args_filterByName, each_file)
                        if args_filterByName in each_file:
                            tmp_allfilename.append(each_file)
                    allfilename = tmp_allfilename
                return jsonify({
                    'isDirectory': os.path.isdir(dir),
                    'file': allfilename
                }), 201
        else:
            print('file not exist!')
            return abort(404)
    if request.method == 'POST':
        print('methods is POST')
        if os.path.isfile(dir):
            print('file is already exists!')
            return abort(404)
        else:
            path_split = str(path).split('/')
            for each_dir in path_split[:-1]:
                newdir = newdir+'\\'+each_dir
                print('new dir is:', newdir)
                if os.path.isdir(newdir):
                    print('dir is exists!')
                else:
                    os.mkdir(newdir)
                    print('make new dir in post')
            print(path_split)
            f = open(dir, 'w')
            print('make new file successful')
            f.close()
            return jsonify({
                'file_name': path,
                'content': ''
            }), 201
    if request.method == 'PATCH':
        print('request is patch')
        if os.path.isfile(dir):
            print('path exist!')
            return jsonify({
                'file_name': path,
                'request.method': 'patch'
            }), 201
        else:
            return abort(404)
    if request.method == 'DELETE':
        print('request is delete')
        if os.path.isfile(dir):
            print('path exist!')
            os.remove(dir)
            print('remove file success!')
            return jsonify({
                'file_name': path,
                'request.method': 'delete'
            }), 201
        else:
            return abort(404)


# 建立API路由products，並將該路由導向Products物件
api.add_resource(Products, '/products')

if __name__ == "__main__":
    app.run(port=8088, debug=True)
