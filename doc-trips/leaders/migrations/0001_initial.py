# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import leaders.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('db', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaderApplication',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('status', models.CharField(max_length=4, default='PEND', choices=[('PEND', 'Pending'), ('ACC', 'Accepted'), ('WAIT', 'Waitlisted'), ('REJ', 'Rejected'), ('CROO', 'Croo'), ('CANC', 'Cancelled'), ('DEP', 'Deprecated'), ('DISQ', 'Disqualified')], verbose_name='Application status')),
                ('class_year', models.PositiveIntegerField()),
                ('gender', models.CharField(max_length=25)),
                ('hinman_box', models.CharField(max_length=10)),
                ('phone', models.CharField(max_length=255, verbose_name='Phone number')),
                ('from_where', models.CharField(max_length=255, verbose_name='Where are you from?')),
                ('what_do_you_like_to_study', models.CharField(max_length=255, verbose_name='What do you like to study?')),
                ('tshirt_size', models.CharField(max_length=2, choices=[('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('XL', 'Extra large')])),
                ('dietary_restrictions', models.TextField(verbose_name='Do you have any dietary restrictions or allergies that we should know about?', blank=True)),
                ('allergen_information', models.TextField(verbose_name='What happens if you come into contact with this allergen (e.g. I turn purple and squishy if I eat a grape!)?', blank=True)),
                ('trippee_confidentiality', models.BooleanField(default=False, verbose_name="If selected to be a DOC Trips Leader, I understand that I will be given access to my Trippees' confidential medical information for safety purposes. I pledge to maintain the confidentiality of this information, except as is required by medical or legal concerns")),
                ('in_goodstanding_with_college', models.BooleanField(default=False, verbose_name='By applying to lead a DOC Trip, I acknowledge that I am in good standing with the College. This may be verified by DOC Trips through the Undergraduate Dean’s Office.')),
                ('trip_preference_comments', models.TextField(verbose_name='Looking at the Trips descriptions, please feel free to use this space to address any concerns or explain your availability. This will only be used to help us in Trip assignments, it will not be considered when your application is being read.', blank=True)),
                ('personal_activities', models.TextField(verbose_name='Please list your primary activities and involvements at Dartmouth and beyond', blank=True)),
                ('personal_communities', models.TextField(verbose_name='Are there any communities with which you identify? You are welcome to list more than one, or leave this blank. Be as brief or detailed as you’d like.', blank=True)),
                ('went_on_trip', models.BooleanField(default=False, verbose_name='Did you go on a First Year Trip?')),
                ('applied_to_trips', models.BooleanField(default=False, verbose_name='Have you applied to lead a Trip before?')),
                ('is_in_hanover_this_fall', models.BooleanField(default=False, verbose_name='Are you planning to be in Hanover this fall?')),
                ('tell_us_about_yourself', models.TextField(verbose_name='Without simply listing activities, tell us about yourself. What are you passionate about? What identities are meaningful to you? Feel free to answer this question in the way most comfortable for you.', blank=True)),
                ('comforting_experience', models.TextField(verbose_name='Describe an experience in which someone else (a friend, roommate, classmate, etc.) felt uncomfortable. What did you do to make them feel more comfortable and welcome in that environment?', blank=True)),
                ('best_compliment', models.TextField(verbose_name='What is the best compliment (serious, funny, reflective, goofy, etc.) you have ever received (or wish you had received)?', blank=True)),
                ('trip_leader_roles', models.TextField(verbose_name='What role do trip leaders play in the broader purpose(s) of DOC Trips? How will you, as a trip leader, further these goals both during your trip as well as back on campus?', blank=True)),
                ('what_to_change_about_trips', models.TextField(verbose_name='If you have led a DOC Trip before, what would you change about the program (big or small)? If you have not led a DOC Trip before, what would you change about the program (big or small) OR what would you change about your introduction to Dartmouth?', blank=True)),
                ('leadership_experience', models.TextField(verbose_name='Describe a leadership experience you had (in high school, at Dartmouth, as a former trip leader, etc.). What specific skills and insights did you bring to that experience? How would you describe yourself as a leader?', blank=True)),
                ('working_with_difference', models.TextField(verbose_name='Discuss a situation (in high school, at Dartmouth, on an off-term, etc.) in which you had to work with someone who was very different from yourself. How did you respond to these differences?', blank=True)),
                ('coleader_qualities', models.TextField(verbose_name='Trip leaders work closely with their co-leader before, during, and after the trip. What qualities would you value in a co-leader that both balance your weaknesses AND complement your strengths?', blank=True)),
                ('why_do_you_want_to_be_involved', models.TextField(verbose_name='Why do you want to be involved in First-Year Trips as a trip leader?', blank=True)),
                ('medical_certifications', models.TextField(verbose_name="Current certifications in Standard First Aid and CPR are required for all DOC trip leaders. Please list any relevant medical certifications you hold or have held, along with the program that sponsored the certification and the dates they expire — for example, 'First Aid (American Red Cross), expires October 2013'.", blank=True)),
                ('relevant_experience', models.TextField(verbose_name='For each type of trip you are interested in leading, please describe your level of expertise and any amount of previous experience that might qualify you to lead that particular trip. Include any accomplishments, special skills, or certifications that you consider relevant (lifeguard training, yoga experience, mountain biking enthusiast, photography class, NOLS, skiing since you were a baby, etc.). No experience is completely fine! — our training will prepare you for just about anything you might encounter and you will be paired will a leader who complements your skill set.', blank=True)),
                ('cannot_participate_in', models.TextField(verbose_name='If applicable, please elaborate (to the extent you feel comfortable) on any particular trips or activities that you absolutely cannot participate in. This information will be used exclusively for trip assignments & co-leader pairings. *NOTE: All information in this application will remain confidential.', blank=True)),
                ('spring_leader_training_ok', models.BooleanField(default=False, verbose_name='I can attend Leader Training during the spring term.')),
                ('summer_leader_training_ok', models.BooleanField(default=False, verbose_name='I can attend Leader Training during the summer term.')),
                ('express_yourself', models.TextField(verbose_name='It’s always tough to say everything you want to in an application – so this is an opportunity to share any additional thoughts or information. If you’ve said enough, then feel free to leave this portion blank!', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LeaderGrade',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('grade', models.DecimalField(validators=[leaders.models.validate_grade], decimal_places=1, max_digits=3)),
                ('comment', models.CharField(max_length=255)),
                ('hard_skills', models.BooleanField(default=False)),
                ('soft_skills', models.BooleanField(default=False)),
                ('grader', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('leader_application', models.ForeignKey(related_name='grades', to='leaders.LeaderApplication')),
                ('trips_year', models.ForeignKey(to='db.TripsYear', editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
