from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.contact import Contact
from app.schemas.contact import ContactSchema
import json
from sqlalchemy import or_

contacts_bp = Blueprint('contacts', __name__)
contact_schema = ContactSchema()
contacts_schema = ContactSchema(many=True)

@contacts_bp.route('/', methods=['POST'])
@jwt_required()
def create_contact():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    # Validate input data
    errors = contact_schema.validate(data)
    if errors:
        return jsonify({'error': errors}), 400
    
    # Handle phone numbers
    phone_numbers = json.dumps(data.get('phone_numbers', []))
    
    # Create new contact
    contact = Contact(
        user_id=current_user_id,
        first_name=data['first_name'],
        last_name=data['last_name'],
        address=data.get('address'),
        company=data.get('company'),
        phone_numbers=phone_numbers
    )
    
    db.session.add(contact)
    db.session.commit()
    
    return jsonify({
        'message': 'Contact created successfully',
        'contact': contact_schema.dump(contact)
    }), 201

@contacts_bp.route('/', methods=['GET'])
@jwt_required()
def get_contacts():
    current_user_id = get_jwt_identity()
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    # Build query
    query = Contact.query.filter_by(user_id=current_user_id)
    
    # Add search filter if provided
    if search:
        search_filter = or_(
            Contact.first_name.ilike(f'%{search}%'),
            Contact.last_name.ilike(f'%{search}%'),
            Contact.company.ilike(f'%{search}%')
        )
        query = query.filter(search_filter)
    
    # Execute query with pagination
    paginated_contacts = query.order_by(Contact.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # Prepare response
    result = {
        'contacts': contacts_schema.dump(paginated_contacts.items),
        'page': page,
        'per_page': per_page,
        'total': paginated_contacts.total,
        'pages': paginated_contacts.pages
    }
    
    return jsonify(result), 200

@contacts_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_contact(id):
    current_user_id = get_jwt_identity()
    
    contact = Contact.query.filter_by(id=id, user_id=current_user_id).first()
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    return jsonify(contact_schema.dump(contact)), 200

@contacts_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_contact(id):
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    # Validate input data
    errors = contact_schema.validate(data)
    if errors:
        return jsonify({'error': errors}), 400
    
    # Find contact
    contact = Contact.query.filter_by(id=id, user_id=current_user_id).first()
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    # Update contact
    contact.first_name = data['first_name']
    contact.last_name = data['last_name']
    contact.address = data.get('address')
    contact.company = data.get('company')
    contact.phone_numbers = json.dumps(data.get('phone_numbers', []))
    
    db.session.commit()
    
    return jsonify({
        'message': 'Contact updated successfully',
        'contact': contact_schema.dump(contact)
    }), 200

@contacts_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_contact(id):
    current_user_id = get_jwt_identity()
    
    contact = Contact.query.filter_by(id=id, user_id=current_user_id).first()
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    db.session.delete(contact)
    db.session.commit()
    
    return jsonify({'message': 'Contact deleted successfully'}), 200