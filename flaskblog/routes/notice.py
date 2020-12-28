from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required

from flaskblog import app, db
from flaskblog.forms import NoticeForm
from flaskblog.models import Notice


@app.route("/notice/new", methods=['GET', 'POST'])
@login_required
def new_notice():
  form = NoticeForm()
  if form.validate_on_submit():
    notice = Notice(title=form.title.data, content=form.content.data,
                  author=current_user)
    db.session.add(notice)
    db.session.commit()
    flash(f'your Notice has been created', 'success')
    return redirect(url_for('home'))
  return render_template('new_notice.html', title='new notice', legend='Notice',
                         form=form)


@app.route("/notice/<int:notice_id>", methods=['GET', 'POST'])
def notice(notice_id):
  notice = Notice.query.get_or_404(notice_id)
  return render_template('notice.html', title=notice.title, notice=notice)


@app.route("/notice/<int:notice_id>/update", methods=['GET', 'POST'])
@login_required
def update_notice(notice_id):
  notice = Notice.query.get_or_404(notice_id)
  if notice.author != current_user:
    abort(403)
  form = NoticeForm()
  form.title.data = notice.title
  form.content.data = notice.content
  if form.validate_on_submit():
    notice.title = form.title.data
    notice.content = form.content.data
    db.session.commit()
    flash('Your notice has been updated!', 'success')
    return redirect(url_for('notice', notice_id=notice.id))
  return render_template('notice.html', title='Update Notice',
                         form=form, legend='Update Notice')


@app.route("/notice/<int:notice_id>/delete", methods=['POST'])
@login_required
def delete_notice(notice_id):
  notice = Notice.query.get_or_404(notice_id)
  if notice.author != current_user:
    abort(403)
  db.session.delete(notice)
  db.session.commit()
  flash(f'Your notice has been deleted!', 'success')
  return redirect(url_for('notice.html'))
