from flask import Blueprint,render_template

errors=Blueprint('errors',__name__)



@errors.app_errorhandler(404)

def err0r_404(error):
	return render_template('errors/404.html'),404


@errors.app_errorhandler(403)

def err0r_403(error):
	return render_template('errors/403.html'),403

@errors.app_errorhandler(500)

def err0r_500(error):
	return render_template('errors/500.html'),500