# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leader', '0014_auto_20140912_1719'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leaderapplication',
            name='notes',
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='allergen_information',
            field=models.TextField(default='', blank=True, verbose_name='What happens if you come into contact with this allergen (e.g. I turn purple and squishy if I eat a grape!)?'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='best_compliment',
            field=models.TextField(default='', blank=True, verbose_name='What is the best compliment (serious, funny, reflective, goofy, etc.) you have ever received (or wish you had received)?'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='cannot_participate_in',
            field=models.TextField(default='', blank=True, verbose_name='If applicable, please elaborate (to the extent you feel comfortable) on any particular trips or activities that you absolutely cannot participate in. This information will be used exclusively for trip assignments & co-leader pairings. *NOTE: All information in this application will remain confidential.'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='coleader_qualities',
            field=models.TextField(default='', blank=True, verbose_name='Trip leaders work closely with their co-leader before, during, and after the trip. What qualities would you value in a co-leader that both balance your weaknesses AND complement your strengths?'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='comforting_experience',
            field=models.TextField(default='', blank=True, verbose_name='Describe an experience in which someone else (a friend, roommate, classmate, etc.) felt uncomfortable. What did you do to make them feel more comfortable and welcome in that environment?'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='dietary_restrictions',
            field=models.TextField(default='', blank=True, verbose_name='Do you have any dietary restrictions or allergies that we should know about? (We use this information for packing food for Trips and it will not affect your candidacy.)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='express_yourself',
            field=models.TextField(default='', blank=True, verbose_name='It’s always tough to say everything you want to in an application – so this is an opportunity to share any additional thoughts or information. If you’ve said enough, then feel free to leave this portion blank!'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='leadership_experience',
            field=models.TextField(default='', blank=True, verbose_name='Describe a leadership experience you had (in high school, at Dartmouth, as a former trip leader, etc.). What specific skills and insights did you bring to that experience? How would you describe yourself as a leader?'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='medical_certifications',
            field=models.TextField(default='', blank=True, verbose_name="Current certifications in Standard First Aid and CPR are required for all DOC trip leaders. Please list any relevant medical certifications you hold or have held, along with the program that sponsored the certification and the dates they expire — for example, 'First Aid (American Red Cross), expires October 2013'."),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='relevant_experience',
            field=models.TextField(default='', blank=True, verbose_name='For each type of trip you are interested in leading, please describe your level of expertise and any amount of previous experience that might qualify you to lead that particular trip. Include any accomplishments, special skills, or certifications that you consider relevant (lifeguard training, yoga experience, mountain biking enthusiast, photography class, NOLS, skiing since you were a baby, etc.). No experience is completely fine! — our training will prepare you for just about anything you might encounter and you will be paired will a leader who complements your skill set.'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='spring_leader_training_ok',
            field=models.BooleanField(default=False, verbose_name='Can you attend Leader Training during the spring term?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='summer_leader_training_ok',
            field=models.BooleanField(default=False, verbose_name='Can you attend Leader Training during the summer term?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='trip_leader_roles',
            field=models.TextField(default='', blank=True, verbose_name='What role do trip leaders play in the broader purpose(s) of DOC Trips? How will you, as a trip leader, further these goals both during your trip as well as back on campus?'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='what_to_change_about_trips',
            field=models.TextField(default='', blank=True, verbose_name='If you have led a DOC Trip before, what would you change about the program (big or small)? If you have not led a DOC Trip before, what would you change about the program (big or small) OR what would you change about your introduction to Dartmouth? *NOTE: No prior experience is necessary to lead a trip.'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='why_do_you_want_to_be_involved',
            field=models.TextField(default='', blank=True, verbose_name='Why do you want to be involved in First-Year Trips as a trip leader?'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='leaderapplication',
            name='working_with_difference',
            field=models.TextField(default='', blank=True, verbose_name='Discuss a situation (in high school, at Dartmouth, on an off-term, etc.) in which you had to work with someone who was very different from yourself. How did you respond to these differences?'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='personal_communities',
            field=models.TextField(blank=True, verbose_name='Are there any communities with which you identify? You are welcome to list more than one, or leave this blank. Be as brief or detailed as you’d like.'),
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='tell_us_about_yourself',
            field=models.TextField(blank=True, verbose_name='Without simply listing activities, tell us about yourself. What are you passionate about? What identities are meaningful to you? Feel free to answer this question in the way most comfortable for you.'),
        ),
        migrations.AlterField(
            model_name='leaderapplication',
            name='trip_preference_comments',
            field=models.TextField(blank=True, verbose_name='Comments'),
        ),
    ]
