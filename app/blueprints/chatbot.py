from datetime import date

from flask import Blueprint, current_app, jsonify, render_template, request, session

from app.models.appointment import Appointment
from app.models.medical_record import MedicalRecord
from app.utils.decorators import login_required
from app.utils.gemini import GeminiError, generate_response


chatbot = Blueprint('chatbot', __name__)

SYSTEM_PROMPT = """You are MediCare's patient health assistant.
Use only the patient information included in the conversation.
You may also answer general health-education questions about diseases and
medical conditions, including what they are, common causes, why they occur,
and commonly reported symptoms. Clearly label this as general information,
not a diagnosis. Do not claim that the patient has a disease based on symptoms
or records. If a question is unrelated to healthcare or cannot be answered
from the patient's records when it asks for patient-specific information,
reply exactly: "I don't know about it, contact a professional."
Do not automatically provide a complete summary. First understand what the
patient is asking for. If the request is vague, ask a short clarifying question
and offer choices such as upcoming appointments, past appointments, doctor
notes, documented treatments, medical records, or a complete summary.
Answer only the requested part. Clearly distinguish documented facts from
missing information and never invent a diagnosis, medicine, dosage, or treatment.
You are not a doctor and must not provide emergency or personalized medical
advice, diagnose the patient, or prescribe medicines. For urgent or severe
symptoms, tell the patient to contact a doctor or emergency services.

Format every response in clean Markdown:
- Use a short heading when useful.
- Use bullet points for multiple items.
- Use bold labels for dates, doctors, statuses, and treatment names.
- Keep paragraphs short and do not repeat the entire patient history."""


def _patient_context(user_id: int) -> str:
    appointments = (
        Appointment.query
        .filter_by(user_id=user_id)
        .order_by(Appointment.date.desc(), Appointment.time_slot.desc())
        .all()
    )
    records = (
        MedicalRecord.query
        .filter_by(user_id=user_id)
        .order_by(MedicalRecord.created_at.desc())
        .all()
    )

    lines = ['PATIENT APPOINTMENTS:']
    if appointments:
        for appt in appointments:
            lines.append(
                f'- Date: {appt.date.isoformat()}, time: {appt.time_slot}, '
                f'doctor: Dr. {appt.doctor.name}, specialty: '
                f'{appt.doctor.specialization}, status: {appt.status}, '
                f'patient reason: {appt.reason or "Not provided"}, '
                f'doctor notes: {appt.notes or "No doctor notes"}'
            )
    else:
        lines.append('- No appointments found.')

    lines.append('MEDICAL RECORDS:')
    if records:
        for record in records:
            lines.append(
                f'- Date: {record.created_at.date().isoformat()}, '
                f'type: {record.record_type}, title: {record.title}, '
                f'notes: {record.notes or "No notes"}'
            )
    else:
        lines.append('- No medical records found.')

    return '\n'.join(lines)


@chatbot.route('/chatbot')
@login_required
def page():
    return render_template('user/chatbot.html')


@chatbot.route('/chatbot/message', methods=['POST'])
@login_required
def message():
    data = request.get_json(silent=True) or {}
    user_message = str(data.get('message', '')).strip()
    if not user_message:
        return jsonify({'error': 'Please enter a question.'}), 400
    if len(user_message) > 2000:
        return jsonify({'error': 'Please keep your question under 2,000 characters.'}), 400

    prompt = (
        f'Today is {date.today().isoformat()}.\n\n'
        f'{_patient_context(session["user_id"])}\n\n'
        f'PATIENT QUESTION:\n{user_message}'
    )
    try:
        answer = generate_response(
            current_app.config['GEMINI_API_KEY'],
            current_app.config['GEMINI_MODEL'],
            SYSTEM_PROMPT,
            prompt,
        )
    except GeminiError as exc:
        current_app.logger.warning('Chatbot request failed: %s', exc)
        return jsonify({'error': str(exc)}), 503

    return jsonify({'answer': answer})
