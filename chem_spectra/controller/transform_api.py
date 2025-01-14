import json
from flask import (
    Blueprint, request, send_file, make_response,
)
# from chem_spectra.controller.helper.settings import get_ip_white_list
from chem_spectra.controller.helper.file_container import FileContainer
from chem_spectra.controller.helper.share import (
    to_zip_response, extract_params
)

from chem_spectra.model.transformer import TransformerModel as TraModel


trans_api = Blueprint('transform_api', __name__)


@trans_api.before_app_request
def filter_remote_ip():
    pass
    # trusted_servers = get_ip_white_list()
    # if request.remote_addr not in trusted_servers:
    #     abort(403)


@trans_api.route('/zip_jcamp_n_img', methods=['POST'])
def zip_jcamp_n_img():
    file = FileContainer(request.files['file'])
    molfile = FileContainer(request.files.get('molfile'))
    params = extract_params(request)
    if file:  # and allowed_file(file):
        cmpsr = TraModel(file, molfile=molfile, params=params).to_composer()
        if ((type(cmpsr) is dict) and "invalid_molfile" in cmpsr):
            return json.dumps(cmpsr)
        tf_jcamp, tf_img = cmpsr.tf_jcamp(), cmpsr.tf_img()
        spc_type = cmpsr.core.ncl if cmpsr.core.typ == 'NMR' else cmpsr.core.typ
        memory = to_zip_response([tf_jcamp, tf_img])
        rsp = make_response(
            send_file(
                memory,
                attachment_filename='spectrum.zip',
                as_attachment=True
            )
        )
        rsp.headers['X-Extra-Info-JSON'] = json.dumps({'spc_type': spc_type})
        return rsp


@trans_api.route('/zip_jcamp', methods=['POST'])
def zip_jcamp():
    file = FileContainer(request.files['file'])
    molfile = FileContainer(request.files.get('molfile'))
    params = extract_params(request)
    if file:  # and allowed_file(file):
        tf_jcamp = TraModel(file, molfile=molfile, params=params).convert2jcamp()
        memory = to_zip_response([tf_jcamp])
        return send_file(
            memory,
            attachment_filename='spectrum.zip',
            as_attachment=True
        )


@trans_api.route('/zip_image', methods=['POST'])
def zip_image():
    file = FileContainer(request.files['file'])
    molfile = FileContainer(request.files.get('molfile'))
    params = extract_params(request)
    if file:  # and allowed_file(file):
        tf_img = TraModel(file, molfile=molfile, params=params).convert2img()
        memory = to_zip_response([tf_img])
        return send_file(
            memory,
            attachment_filename='spectrum.zip',
            as_attachment=True
        )


@trans_api.route('/jcamp', methods=['POST'])
def jcamp():
    file = FileContainer(request.files['file'])
    molfile = FileContainer(request.files.get('molfile'))
    params = extract_params(request)
    if file:  # and allowed_file(file):
        tf_jcamp = TraModel(file, molfile=molfile, params=params).convert2jcamp()
        return send_file(
            tf_jcamp,
            attachment_filename='spectrum.jdx',
            as_attachment=True
        )


@trans_api.route('/image', methods=['POST'])
def image():
    file = FileContainer(request.files['file'])
    molfile = FileContainer(request.files.get('molfile'))
    params = extract_params(request)
    if file:  # and allowed_file(file):
        tf_img = TraModel(file, molfile=molfile, params=params).convert2img()
        return send_file(
            tf_img,
            attachment_filename='spectrum.png',
            as_attachment=True,
            mimetype='image/png'
        )
