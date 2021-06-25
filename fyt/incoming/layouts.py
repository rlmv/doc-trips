from crispy_forms.layout import HTML, Div, Field, Fieldset, Layout, Row, Submit

from fyt.utils.fmt import join_with_and, section_range


"""
crispy_form layouts
"""


class RegistrationFormLayout(Layout):
    def __init__(self, section_fields, triptype_fields, **kwargs):

        local_sections = join_with_and(kwargs['local_sections'])
        local_sections_range = section_range(kwargs['local_sections'])
        not_local_sections = join_with_and(kwargs['not_local_sections'])
        not_local_sections_range = section_range(kwargs['not_local_sections'])
        international_sections = join_with_and(kwargs['international_sections'])
        trips_cost = str(kwargs['trips_cost'])
        contact_url = kwargs['contact_url']
        doc_membership_cost = str(kwargs['doc_membership_cost'])

        super().__init__(
            Fieldset(
                'Mission',
                HTML(
                    '<p>First-Year Trips is a pre-orientation experience which aims to  '
                    'support the transition of incoming students to Dartmouth, while '
                    'fostering a sense of belonging and empowerment for all new members of the Dartmouth community. '
                    'First-Year Trips collaborates with New Student Orientation and Outdoor Programs '
                    'to provide peer-led, small-group connections in the spaces and places within and surrounding Dartmouth’s campus. '
                ),
            ),
            Fieldset(
                'General Information',
                'name',
                'gender',
                # show existing contact info?
                # TODO: address contact info
                'previous_school',
                'phone',
                'email',
                'guardian_email',
            ),
            Fieldset(
                'Orientations and Pre-Season Training',
                HTML(
                    "<p> The College has several different pre-orientation options, including athletics pre-season for fall sports. ALL students are able to participate in First-Year Trips, even if they are involved in other pre-orientation programs. We work with other programs and offices as we schedule the Trips program, so the information below is helpful in assigning you to an appropriately scheduled trip. </p>"
                    "<p> If your group is limited to certain sections, be sure to mark all other sections as 'Not Available' (see below). Please note that marking any of these groups will NOT affect your eligibility to participate in First-Year Trips.</p>"
                ),
                'is_exchange',
                'is_transfer',
                'is_international',
                'is_native',
                'is_fysep',
                'is_athlete',
            ),
            Fieldset(
                'Section',
                HTML(
                    "<p>Because we can’t have a thousand students all arrive on the same day, we stagger our program over ten Sections.</p>"
                    "<p> "
                    + local_sections
                    + " are for students who live within a few hours drive of Hanover, NH and can return home after their trip. They then come back to campus on the College's official move-in day. If you live in the Northeast United States, please try to be available for as many of these sections as possible. First-Year Trips provides bus service to several parts of the Northeast U.S. for these specific sections, so check out the 'Bus Option' below. </p>"
                    "<p> "
                    + not_local_sections
                    + " are for students who do not live nearby, and couldn’t reasonably return home between their trip and the College's official move-in day. These students will be able to store their belongings in their dorm rooms when they arrive (although they WILL NOT be staying there until their DOC Trip is over). We will provide lodging for the duration of First-Year Trips. Students on sections "
                    + not_local_sections_range
                    + " can move into their rooms when their trip returns to campus (even though some return before official move-in day).</p>"
                    "<p> "
                    + international_sections
                    + " are the sections for international students. Signing up for these sections as an international student will ensure you are able to move-in to your residence hall the day before your trip (ONLY international students can do this), you are not expected to go home after your Trip. By selecting these sections, you will return from your trip in time for the start of International Student Orientation. </p> "
                    "<p>Pull out your calendar for this! Confirm the dates of "
                    "family activities, work schedules, and other commitments. "
                    "<strong> Please select all sections you "
                    "would be available for unless you have a specific reason "
                    "that you would not be available.</strong> Once your "
                    "section has been assigned it is incredibly difficult for "
                    "us to change it!</p>"
                ),
                Layout(*section_fields),
                HTML(
                    "<p> If you have a particular, immovable scheduling conflict and need to come on a specific section, please elaborate below. Let us know which section(s) you can attend and which ones you cannot. </p>"
                ),
                Field('schedule_conflicts', rows=3),
            ),
            Fieldset(
                'Accommodations',
                HTML(
                    "<p> We recognize that some students may need additional accommodations related (but not limited) to disabilities, religious practices, dietary restrictions, allergies, and other needs. We are committed to doing everything possible to help all students participate in the Trips program to the extent they feel comfortable. (e.g. electricity can be provided if you require a medical device). Please let us know of your needs on your registration form; all information is kept confidential. You may also contact the Student Accessibility Services Office by phone at (603) 646.9900. </p>"
                ),
            ),
            Fieldset(
                'Trip Type',
                HTML(
                    "<p> Every trip spends time exploring a part of New Hampshire or Vermont while doing any number of activities - everything from hiking to yoga to kayaking to organic farming to ecology. We will work with you to match you to something that you feel is exciting and comfortable. </p>"
                    "<p> We offer a variety of types of trip, each corresponding to another activity. {% include 'incoming/_triptype_modal.html' %} </p>"
                    "<p> You must list a Hiking or Cabin Camping trip as one of your possible choices - those are the most common trip types we offer. If that sounds scary to you, don’t worry! We offer these activities in areas, facilities, and intensities that can accommodate anyone. If you have a specific concern about accessibility or ability, please reach out to us! We will work with you to meet your needs, whatever they may be. </p>"
                    "<p> In our process, we do our very best to assign you to a trip you have listed as either your first choice or a preferred option. If you are not assigned your first choice, we encourage you to check out the beginner classes & trips offered by the Dartmouth Outing Club throughout the school year. </p>"
                ),
                *triptype_fields
            ),
            Fieldset(
                'T-Shirts',
                HTML(
                    "<p> As part of going on Trips, you get a T-Shirt! They’re uniquely designed for students every year (and we like to think they’re pretty neat). What size would you like (US Unisex sizes)? </p>"
                ),
                'tshirt_size',
            ),
            Fieldset(
                'Medical Information',
                HTML(
                    "<p> This will absolutely NOT affect your ability to go on a Trip. While many students manage their own health needs, we would prefer that you let us know of any needs or conditions including (but not limited to) allergies, dietary restrictions, and chronic illnesses. We are able to accommodate any accessibility need (e.g. we can provide electricity if you require a medical device, etc.). We encourage you to provide as much detail as possible on your registration form. All information will be kept confidential. Please contact us if you would like to discuss any accommodations. You may also contact the Student Accessibility Services Office by phone at (603) 646.9900. </p>"
                    "<p> If you do have any medical problem(s) which may become aggravated in the outdoors, it is your responsibility to consult with your doctor (before your trip begins) for instructions or medication. We're happy to provide additional details about your trip's itinerary if needed. </p>"
                    "<p> We encourage you to elaborate on any conditions on the registration form, however the online form is <strong>not</strong> a secure form so we cannot guarantee the confidentiality of medical information. If you would prefer to explain any conditions to us over the phone, please feel free to call us at (603) 646-3996. </p>"
                ),
                Field('food_allergies', rows=3),
                Field('dietary_restrictions', rows=3),
                Field('medical_conditions', rows=3),
                'epipen',
                Field('needs', rows=3),
            ),
            Fieldset(
                'General Physical Condition',
                HTML(
                    "<p> We will match you to a trip that best suits your interests and abilities. For this reason, please be specific and detailed in describing your physical condition & outdoors experience on the registration form. We want to challenge you as little or as much as you feel comfortable with. The more information you provide, the better! </p>"
                    "<p> Tell us about your outdoor experience and how much you enjoy physical activity. There are NO right answers - we have trips for everyone, regardless of your prior experience or physical condition. The more we know about what your prior experiences have been and what you hope to do on your trip, the better we can assign you a trip that is both comfortable and fun!</p>"
                ),
                'regular_exercise',
                Field('physical_activities', rows=3),
                Field('other_activities', rows=3),
            ),
            Fieldset(
                'Swimming Experience',
                HTML(
                    "<p> Some First-Year Trips, such as Kayaking, heavily involve water and may involve swimming. Anyone who participates in a Water Trip must complete a 50-meter swim test on their first day of Trips. Here, please rate your swimming ability to help us match you to a Trip! </p>"
                ),
                'swimming_ability',
                HTML(
                    "<p> If you cannot swim or would rather not take the swim test, please indicate that by answering the above question with 'non-swimmer'. Don’t worry -- there are plenty of Trips which don’t involve water. <p>"
                ),
            ),
            Fieldset(
                'Hiking and Camping Experience',
                'camping_experience',
                'hiking_experience',
                Field('hiking_experience_description', rows=3),
            ),
            Fieldset(
                'Canoeing & Kayaking Experience',
                HTML(
                    "<p> Complete this section only if you indicated above that you preferred or were available for a <strong>Canoeing</strong> trip or a <strong>Kayaking</strong> trip. Please note that NO experience is needed for these types of trips; we just want to get a sense of your comfort level with these activites. </p>"
                ),
                'has_boating_experience',
                Field('boating_experience', rows=3),
                Field('other_boating_experience', rows=3),
            ),
            Fieldset(
                'Fishing Experience',
                HTML(
                    "<p> Complete this section only if you indicated above that you preferred or were available for a <strong>Fishing</strong> trip. Fishing experience is NOT required to participate in this trip. </p>"
                ),
                Field('fishing_experience', rows=3),
            ),
            Fieldset(
                'Horseback Riding Experience',
                HTML(
                    "<p> Complete this section only if you indicated above that you preferred or were available for a <strong>Horseback Riding</strong> trip. </p>"
                ),
                Field('horseback_riding_experience', rows=3),
            ),
            Fieldset(
                'Mountain Biking Experience',
                HTML(
                    "<p> Complete this section only if you indicated above that you preferred or were available for a trip that involved <strong>Biking</strong>. Prior mountain biking experience is NOT required to participate in this trip.</p>"
                ),
                Field('mountain_biking_experience', rows=3),
            ),
            Fieldset(
                'Sailing Experience',
                HTML(
                    "<p> Complete this section only if you indicated above that you preferred or were available for a Sailing trip. Sailing experience is NOT required to participate in this trip. </p>"
                ),
                Field('sailing_experience', rows=3),
            ),
            Fieldset('Anything else?', Field('anything_else', rows=3)),
            Fieldset(
                'Gear',
                HTML(
                    "<p>We will use this information to fit gear for you on "
                    "trips that require it (e.g. paddles and life jackets for "
                    "canoeing and kayaking trips, harnesses for climbing "
                    "trips, etc.)</p>"
                ),
                Row(
                    Div('height', css_class='col-sm-3'),
                    Div('weight', css_class='col-sm-3'),
                ),
            ),
            Fieldset(
                'Bus Option',
                HTML(
                    "<p> Students in "
                    + local_sections
                    + " will not be able to move into their rooms after their trips. It is for them that we coordinate bus transportation. We charter buses from various areas of the Northeast to bring students to Hanover for their trips and return them home afterwards. Because of the need to reserve spaces on later sections for those who live farther away, it is essential that all applicants from the Northeast come on Sections "
                    + local_sections_range
                    + ". </p>"
                    "<p><strong> These buses do not pick up at the airport.</strong> They are for students who live in the Northeast, NOT students who will be flying to Boston or Manchester airports. (Transportation from the airport must be arranged on your own.)</p>"
                    "<p>If you live in the Northeast, we ask you to elect the bus option unless: <ul> <li> you are absolutely unavailable for "
                    + local_sections
                    + ", or </li> <li>none of the stops are within 75 miles of you, or </li> <li> you live close enough to have relatively easy transportation to/from Hanover for you and your trip gear </li> </ul> </p>"
                    "<p> Bus fares vary by location (see bus options below for exact price). Financial assistance is available for bus fares. If the cost of transportation/Trips may prevent you from participating, please contact us & we can help! See below for more information. </p>"
                ),
                'bus_stop_round_trip',
                HTML("<p> Or, if you would like to take a bus only one-way:</p>"),
                Row(
                    Div('bus_stop_to_hanover', css_class="col-sm-6"),
                    Div('bus_stop_from_hanover', css_class="col-sm-6"),
                ),
                HTML(
                    '<p> If our bus option does not work for you, there are other public transportation services such as the train (<a href="http://www.amtrak.com/home">Amtrak</a>) or bus (<a href="https://www.greyhound.com/">Greyhound</a>, <a href="http://www.dartmouthcoach.com/">Dartmouth Coach</a>). We consider these options the most environmentally friendly ways to get here, so check them out!</p>'
                ),
            ),
            Fieldset(
                'Financial Assistance',
                HTML(
                    "<p> We are <i>very</i> committed to making Trips available to anyone, regardless of financial need. We offer <strong>generous financial assistance</strong>, which you can request below. Financial assistance is also available for bussing if you are taking a First-Year Trips bus from one of our Northeast stops to Hanover. The cost for First-Year Trips is $"
                    + trips_cost
                    + ". The cost is the same regardless of which trip you are assigned. </p>"
                    "<p> Eligibility for financial assistance is determined "
                    "in conjunction with the College's Financial Aid office. "
                    "If you are requesting financial assistance from Trips, "
                    "please register now and we will notify students receiving "
                    "any financial assistance in July; the balance of the "
                    "program cost will be charged to your tuition bill. Please "
                    "remember that we are committed to making Trips accessible "
                    "to you; if the cost of Trips may prevent you from "
                    "participating, please contact us and we can help!</p>"
                ),
                'financial_assistance',
            ),
            Fieldset(
                'Waiver of Liability',
                HTML(
                    '<p> Please read, review, and indicate your acknowledgment of the following information. If you have any questions or concerns, please feel free to <a href="'
                    + contact_url
                    + '"> contact us.</a> </p>'
                    "<p><strong> This acknowledgment and assumption of risk, hold harmless agreement, release and waiver of liability is a legally binding document. By acknowledging your understanding and agreement, you are waiving certain rights &mdash; including the right to bring a lawsuit if you are injured while participating in this activity.</strong> </p>"
                    "<p> This document is executed in consideration of being able to participate in the D.O.C. Trips Program, sponsored by the Dartmouth Outing Club. I hereby acknowledge that I am aware that there are risks and dangers inherent in the D.O.C. Trips Program, and I hereby agree that I will listen carefully to and follow all instructions and directions and ask questions if I do not understand. I also acknowledge that, despite careful precautions, there are certain inherent dangers and risks of injury in this activity, and I accept those risks and dangers. I further agree, on behalf of myself, and my heirs and assigns, to release and hold harmless Dartmouth College, its officers, agents, employees, successors, and assigns, from and against any and all claims and causes of action arising out of my participation in this activity, except insofar as such claim or cause of action arises from the negligence or intentional acts of Dartmouth College, its officers, agents, or employees. </p>"
                    "<p> If the student is a minor, I further agree to indemnify and hold harmless Dartmouth College from any and all claims which are brought by, or on behalf of Minor, and which are in any way connected with such use or participation by Minor. </p>"
                ),
                'waiver',
            ),
            Fieldset(
                'OPTIONAL: Dartmouth Outing Club Membership',
                HTML(
                    "<p> The DOC is one of Dartmouth's largest student organizations - and the home of First-Year Trips - and offers many opportunities to get outside and enjoy the beautiful areas surrounding campus. Student members are eligible for membership & positions in the various clubs (e.g. Cabin & Trail, Mountaineering Club, Ski Patrol, etc.), qualify for reduced prices for season passes & cabin rentals, and receive a copy of the 'Dartmouth Outing Guide' book. A student career membership is $"
                    + doc_membership_cost
                    + ". Please indicate if you would like to purchase a student career (the duration of your time as a Dartmouth undergraduate) membership. You will receive information later this summer about your membership. <i>Note: this charge, along with the rest of the cost for your Trip, will be placed directly on your first College tuition bill. </i></p>"
                ),
                'doc_membership',
            ),
            Fieldset(
                'OPTIONAL: Green Fund Donation',
                HTML(
                    "<p> As the largest outdoors orientation program in the country, First-Year Trips is committed to being a responsible steward of both natural resources and the environment. Your donation to the Green Fund will go directly toward sustainability initiatives within the program such as locally-sourced food, providing organic cotton t-shirts to all participants, using bio-diesel fuel for Trips transportation, and serving an entirely vegetarian/organic menu during the program. <i>Note: this donation, along with the rest of the cost for your Trip, will be placed directly on your first College tuition bill.</i> </p>"
                ),
                'green_fund_donation',
            ),
            Fieldset('One Final Request', Field('final_request', rows=3)),
            Submit('submit', 'Submit'),
        )
