
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, HTML, Div, Row, Fieldset, Field

from doc.trippees.models import Registration
from doc.trips.models import Section
from doc.transport.models import Stop

def join_with_and(iter):
    l = list(map(str, iter))
    if len(l) == 0:
        return ""
    elif len(l) == 1:
        return l[0]
    return ", ".join(l[:-1]) + " and " + l[-1]


class RegistrationForm(forms.ModelForm):
    
    # TODO: restrict Section and TripType fields to trips_year
    # (and any other ForeignKeys

    # pass the trips_year to the form
    
    class Meta:
        model = Registration

    def __init__(self, *args, **kwargs):
        trips_year = kwargs.pop('trips_year')
        super(RegistrationForm, self).__init__(*args, **kwargs)

        self.fields['bus_stop'].queryset = Stop.objects.external(trips_year)
        
        self.helper = FormHelper(self)
        self.helper.layout = RegistrationFormLayout(trips_year)


class RegistrationFormLayout(Layout):

    def __init__(self, trips_year):

        # TODO: mv this up the call hierarchy?
        local_sections = join_with_and(Section.objects.local(trips_year))
        not_local_sections = join_with_and(Section.objects.not_local(trips_year))
        international_sections = join_with_and(Section.objects.international(trips_year))
        
        super(RegistrationFormLayout, self).__init__(
            HTML("<p><strong>DOC Trips Mission:</strong> DOC First-year Trips exist to give all incoming students an exciting and unforgettable welcome to the Dartmouth community. Trips provides them with an introduction to the College's traditions and spirit, as well as a safe and positive outdoor experience through the Dartmouth Outing Club. Trips creates common ground for first-year students, a space to build lasting friendships and social support systems, and facilitates a connection to dedicated upperclass students who act as mentors and friends at Dartmouth and beyond.</p>"),
            Fieldset(
                'General Information',
                'name',
                'gender',
                # show existing contact info?
                # TODO: address contact info
                'previous_school', 
                'home_phone',
                'cell_phone',
                'email', 
                'guardian_email',
            ),
            Fieldset(
                'Orientations and Pre-Season Training',
                HTML("<p> The College has several different pre-orientation options, including athletics pre-season for fall sports. ALL students are able to participate in DOC Trips, even if they are involved in other pre-orientation programs. We work with other programs and offices as we schedule the Trips program, so the information below is helpful in assigning you to an appropriately scheduled trip. </p>"
                     "<p> If your group is limited to certain sections, be sure to mark all other sections as 'Not Available' (see below). Please note that marking any of these groups will NOT affect your eligibility to participate in DOC Trips.</p>"),
                # TODO
            ),
            Fieldset(
                'Section', 
                HTML("<p>Because we can’t have a thousand students all arrive on the same day, we stagger our program over ten sections.</p>"
                     "<p> " + local_sections + " are for students who live within a few hours drive of Hanover, NH and can return home after their trip. They then come back to campus on the College's official move-in day. If you live in the Northeast United States, please try to be available for at least one, if not more, of these sections. DOC Trips provides bus service to several parts of the Northeast U.S. for these specific sections, so check out the 'Bus Option' below. </p>"
                     "<p> " + not_local_sections + " are for students who do not live nearby, and couldn’t reasonably return home between their trip and the College's official move-in day. These students will be able to store their belongings in their dorm rooms when they arrive (although they WILL NOT be staying there until their DOC Trip is over). We will provide lodging for the duration of DOC Trips. Students can move into their rooms when their trip returns to campus (even though some return before official move-in day).</p>"
                     "<p> " + international_sections + " are the sections highly recommended for international students. Signing up for these sections as an international student will ensure you are able to move-in to your residence hall the day before your trip (ONLY international students can do this), you are not expected to go home after your Trip. By selecting these sections, you will return from your trip in time for the start of international student orientation. </p> "
                     "<p><strong>Pull out your calendar for this! Confirm the dates of other family activities, work schedules, and other commitments. Once your section has been assigned, it is incredibly difficult for us to change it, especially from an earlier section to a later one! </strong></p>"
                 ),
                # TODO : section preferences
                HTML("<p> If you have a particular, immovable scheduling conflict and need to come on a specific section, please elaborate below. Let us know which section(s) you can attend and which ones you cannot. </p>"),
                Field('schedule_conflicts', rows=3),
            ),
            Fieldset(
                'Trip Type',
                HTML("<p> Every trip spends two and a half days exploring a specific location around New Hampshire while doing any number of outdoor activities - everything from hiking to yoga to kayaking to organic farming. No matter which trip you are assigned to, we promise you'll find the experience to be an exciting and comfortable one. </p>"
                     "<p> We offers a variety of different types of trips on each section. The Trip Type is determined by the activity featured on the trip. You must list a Hiking or Cabin Camping trip as one of your possible choices - those are the most common trip types we offer. We do our very best to assign you to a trip you have listed as either your first choice or a preferred option. If you are not assigned your first choice, we encourage you to check out the beginner classes & trips offered by the Dartmouth Outing Club throughout the school year. The likelihood of getting your first choose increases if you: </p>"
                     "<ul> <li>submit all your registration materials by the deadline</li><li>choose trip sections that correspond to your geographic location (Northeast U.S.: sections A-D, Other regions: sections E-J)</li> <li>Select a trip on section B-G (our slightly smaller sections).</li></ul>"
                     "<p><strong> As long as you register by the deadline, when you register makes no difference. Registering early does not increase your chances of getting your desired trip. </strong></p>"
                 ),
                #TODO: 
            ),
            Fieldset(
                'T-Shirts',
                HTML("<p> You'll be getting a DOC Trips t-shirt! These shirts are 100% organic cotton - wahoo! What size would you like? </p>"),
                'tshirt_size',
            ),
            Fieldset(
                'Accomodations',
                HTML("<p> We recognize that some students may need additional accommodations related (but not limited) to disabilities, religious practices, dietary restrictions, allergies, and other needs. We are committed to doing everything possible to help all students participate in the Trips program to the extent they feel comfortable. (e.g. electricity can be provided if you require a medical device). Please let us know of your needs on your registration form; all information is kept confidential. You may also contact the Student Accessibility Services Office by phone at (603) 646.9900. </p>"),
            ),
            Fieldset(
                'Medical Information',
                HTML("<p> This will absolutely NOT affect your ability to go on a Trip. While many students manage their own health needs, we would prefer that you let us know of any needs or conditions including (but not limited to) allergies, dietary restrictions, and chronic illnesses. We are able to accommodate any accessibility need (e.g. we can provide electricity if you require a medical device, etc.). We encourage you to provide as much detail as possible on your registration form. All information will be kept confidential. Please contact us if you would like to discuss any accommodations. You may also contact the Student Accessibility Services Office by phone at (603) 646.9900. </p>"
                     "<p> If you do have any medical problem(s) which may become aggravated in the outdoors, it is your responsibility to consult with your doctor (before your trip begins) for instructions or medication. We're happy to provide additional details about your trip's itinerary if needed. </p>"
                     "<p> We encourage you to elaborate on any conditions on the registration form, however the online form is <strong>not</strong> a secure form so we cannot guarantee the confidentiality of medical information. If you would prefer to explain any conditions to us over the phone, please feel free to call us at (603) 646-3996. </p>"),
                Field('medical_conditions', rows=4),
                Field('allergies', rows=3),
                Field('allergen_information', rows=3),
                Field('needs', rows=3),
            ),
            Fieldset(
                'Dietary Restrictions',
                Field('dietary_restrictions', rows=3),
            ),
            Fieldset(
                'General Physical Condition',
                HTML("<p> We will match you to a trip that best suits your interests and abilities. For this reason, please be specific and detailed in describing your physical condition & outdoors experience on the registration form. We want to challenge you as little or as much as you feel comfortable with. The more information you provide, the better! </p>"
                     "<p> Tell us about your outdoor experience and how much you enjoy physical activity. There are NO right answers - we have trips for everyone, regardless of your prior experience or physical condition. The more we know about what your prior experiences have been and what you hope to do on your trip, the better we can assign you a trip that is both comfortable and fun!</p>" ),
                'regular_exercise',
                Field('physical_activities', rows=3),
                Field('other_activities', rows=3),
                Field('summer_plans', rows=3),
            ),
            Fieldset(
                'Swimming Experience',
                HTML("<p> Completing a 50 yard swim is a Dartmouth graduation requirement, and is also required for participation in some of our trips, so every incoming student will have the opportunity to take a swim test the day they arrive. </p>"),
                'swimming_ability',
                HTML("<p> If you cannot swim or would rather not take the swim test, please indicate that by answering the above question with 'non-swimmer'. Don't worry, there are plenty of chances to complete the 50-yard swim graduation requirement throughout your time at Dartmouth. This way we can assign you to a trip that does not require you to have passed a swim test. <i>And don't worry! Over half the trips don't involve swimming!</i> <p>"),
            ),
            Fieldset(
                'Hiking and Camping Experience',
                'camping_experience',
                'hiking_experience',
                'hiking_experience_description',
            ),
            Fieldset(
                'Canoeing & Kayaking Experience',
                HTML("<p> Complete this section only if you indicated above that you preferred or were available for a <strong>Canoeing</strong> trip or a <strong>Kayaking</strong> trip. Please note that NO experience is needed for these types of trips; we just want to get a sense of your comfort level with these activites. </p>"),
                'has_boating_experience',
                'boating_experience', 
                'other_boating_experience',
            ),
            Fieldset(
                'Fishing Experience',
                HTML("<p> Complete this section only if you indicated above that you preferred or were available for a <strong>Fishing</strong> trip. Fishing experience is NOT required to participate in this trip. </p>"),
                'fishing_experience',
            ),
            Fieldset(
                'Horseback Riding Experience',
                HTML("<p> Complete this section only if you indicated above that you preferred or were available for a <strong>Horseback Riding</strong> trip. </p>"),
                'horseback_riding_experience',
            ),
            Fieldset(
                'Mountain Biking Experience',
                HTML("<p> Complete this section only if you indicated above that you preferred or were available for a trip that involved <strong>Biking</strong>. Prior mountain biking experience is NOT required to participate in this trip.</p>"),
                'mountain_biking_experience',
            ),
            Fieldset(
                'Anything else?',
                'anything_else',
            ),
            
            Fieldset(
                'Bus Option',
                HTML("<p> Students in " + local_sections + " will not be able to move into their rooms after their trips. It is for them that we coordinate bus transportation. We charter buses from various areas of the Northeast to bring students to Hanover for their trips and return them home afterwards. Because of the need to reserve spaces on later sections for those who live farther away, it is essential that all applicants from the Northeast elect the bus option and come on " + local_sections + " if at all possible. </p>"
                     "<p><strong> These buses do not pick up at the airport.</strong> They are for students who live in the Northeast, NOT students who will be flying to Boston or Manchester airports. (Transportation from the airport must be arranged on your own.)</p>"
                     "<p>If you live in the Northeast, we ask you to elect the bus option unless: <ul> <li> you are absolutely unavailable for " + local_sections + ", or </li> <li>none of the stops are within 75 miles of you, or </li> <li> you live close enough to have relatively easy transportation to/from Hanover for you and your trip gear </li> </ul> </p>"
                     "<p> Bus fares vary by location (see bus options below for exact price). Financial assistance is available for bus fares. If the cost of transportation/Trips may prevent you from participating, please contact us & we can help! See below for more information. </p>"),
                'bus_stop', 
                HTML('<p> If our bus option does not work for you, there other public transportation services such as the train (<a href="http://www.amtrak.com/home">Amtrak</a>) or bus (<a href="https://www.greyhound.com/">Greyhound</a>, <a href="http://www.dartmouthcoach.com/">Dartmouth Coach</a>). We consider these options the most environmentally friendly ways to get here, so check them out!</p>'),

            ),
            
            Submit('submit', 'Submit'),
        )

class IncomingStudentsForm(forms.Form):

    csv_file = forms.FileField(label='CSV file')

    def __init__(self, *args, **kwargs):

        super(IncomingStudentsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', 'Submit'))
        


