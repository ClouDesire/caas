from flask import Flask, abort, jsonify, render_template, request

from config import SECRET_KEY
import notify
import store


app = Flask(__name__)


@app.errorhandler(401)
def unauthorized(e):
    return jsonify(message=str(e)), 401


@app.before_request
def authenticate():
    if request.endpoint == 'get_html':
        return

    if 'CAAS-Auth-Token' not in request.headers:
        abort(401)

    if request.headers['CAAS-Auth-Token'] != SECRET_KEY:
        abort(401)


@app.route('/<label>', methods=['GET'])
def get(label):
    """
    @api {get} /:label Get counter value
    @apiName GetCounter
    @apiGroup Counter

    @apiParam {String} label Counter label.

    @apiSuccess {Number} counter Current value, 0 if label doesn't exist.
    """
    counter = store.get(label)

    return jsonify(counter=counter)


@app.route('/<label>', methods=['PUT'])
def incr(label):
    """
    @api {put} /:label Increment counter
    @apiName IncrementCounter
    @apiGroup Counter

    @apiParam {String} label Counter label.

    @apiSuccess {Number} counter Current value.
    """
    counter = store.incr(label)
    notify.notify_all(label, counter)
    return jsonify(counter=counter)


@app.route('/<label>/<int:counter>', methods=['POST'])
def set(label, counter):
    """
    @api {post} /:label/:counter Directly set counter value
    @apiName SetCounter
    @apiGroup Counter

    @apiParam {String} label Counter label.
    @apiParam {Number} counter New counter value.

    @apiSuccess {Number} counter Current value.
    """
    store.set(label, counter)
    notify.notify_all(label, counter)
    return jsonify(counter=counter)


@app.route('/<label>', methods=['DELETE'])
def reset(label):
    """
    @api {delete} /:label Reset counter
    @apiName ResetCounter
    @apiGroup Counter

    @apiParam {String} label Counter label.

    @apiSuccess {Number} counter Zero value.
    """
    store.delete(label)
    return jsonify(counter=0)


@app.route('/<label>.html', methods=['GET'])
def get_html(label):
    counter = store.get(label)

    return render_template('counter.html', label=label, counter=counter)


if __name__ == '__main__':
    app.run()
