from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, Event, Poll, PollVote, PollOption, User
from . import db
import json
from datetime import datetime

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    

    if request.method == 'POST':
        title = request.form.get('title')
        start = request.form.get('start')
        end = request.form.get('end')

        if not title or not start or not end:
            flash('Event details are required.', category='error')
        else:
            new_event = Event(title=title, start_date=datetime.fromisoformat(start), end_date=datetime.fromisoformat(end), user_id=current_user.id)
            db.session.add(new_event)
            db.session.commit()
            flash('Event added!', category='success')
    
    userName = User.query.with_entities(User.user_name)
    listLength = User.query.with_entities(User.user_name).count()

    return render_template("home.html", user=current_user, users = userName, listLength = listLength)





@views.route('/create_group', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        
        addedUser = request.form.get('addedUser')
        
    return redirect(url_for('views.home'))





@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})



@views.route('/calendar')
@login_required
def calendar():
    events = Event.query.filter_by(user_id=current_user.id).all()
    event_data = [
        {
            'title': event.title,
            'start': event.start_date.isoformat(),
            'end': event.end_date.isoformat()
            
        }
        for event in events
    ]
    return jsonify(event_data)



@views.route('/random-event')
def random_event():
    return render_template('random_event.html')

@views.route('/create-poll', methods=['GET', 'POST'])
@login_required
def create_poll():
    if request.method == 'POST':
        question = request.form.get('question')
        options = [request.form.get('option1'), request.form.get('option2')]
        
        i = 3
        while f'option{i}' in request.form:
            options.append(request.form.get(f'option{i}'))
            i += 1

        if not question or len(options) < 2:
            flash('Please provide a question and at least two options.', 'error')
        else:
            new_poll = Poll(question=question, user_id=current_user.id)
            db.session.add(new_poll)
            db.session.commit()

            for option_text in options:
                new_option = PollOption(option=option_text, poll=new_poll)
                db.session.add(new_option)

            db.session.commit()
            flash('Poll created successfully!', 'success')
            return redirect(url_for('views.show_poll', poll_id=new_poll.id))

    return render_template('create_poll.html')



@views.route('/polls/<int:poll_id>', methods=['GET', 'POST'])
@login_required
def show_poll(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    
    # Query the database to count the number of votes for each option
    for option in poll.options:
        vote_count = PollVote.query.filter_by(option_id=option.id).count()
        option.vote_count = f"- {vote_count}"  # Format vote count string with a dash

    if request.method == 'POST':
        option_id = request.form.get('option')
        if option_id:
            existing_vote = PollVote.query.filter_by(user_id=current_user.id, option_id=option_id).first()
            if existing_vote:
                flash('You have already voted in this poll.', 'error')
            else:
                new_vote = PollVote(user_id=current_user.id, option_id=option_id)
                db.session.add(new_vote)
                db.session.commit()
                flash('Your vote has been recorded.', 'success')
        else:
            flash('Please select an option to vote.', 'error')

        # Redirect to view polls after the vote has been recorded
        return redirect(url_for('views.view_polls'))

    return render_template('poll.html', poll=poll)


@views.route('/view-polls', methods=['GET'])
@login_required
def view_polls():
    # Check if the user is logged in
    if not current_user.is_authenticated:
        # If not logged in, redirect to the login page
        return redirect(url_for('auth.login'))

    # Retrieve polls created by the current user
    user_polls = Poll.query.filter_by(user_id=current_user.id).all()

    return render_template('view_polls.html', polls=user_polls)





@views.route('/discussions', methods=['GET', 'POST']) 
@login_required
def discussions():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('comment is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Sent', category='success')

    return render_template("discussions.html", user=current_user)