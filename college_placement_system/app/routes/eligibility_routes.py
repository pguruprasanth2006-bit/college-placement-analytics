from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.auth import login_required
from app.models import Company
from app.services.eligibility_service import EligibilityService

eligibility_bp = Blueprint('eligibility', __name__)


@eligibility_bp.route('/', methods=['GET'])
@login_required
def index():
    """Eligibility dashboard allowing admin to select a company and view categorized pools."""
    companies = Company.query.order_by(Company.company_name.asc()).all()
    selected_company_id = request.args.get('company_id', type=int)

    result = None
    if selected_company_id:
        result = EligibilityService.evaluate_company_pool(selected_company_id)
        if 'error' in result:
            flash(result['error'], 'danger')
            return redirect(url_for('eligibility.index'))

    return render_template(
        'eligibility.html',
        companies=companies,
        selected_company_id=selected_company_id,
        result=result
    )

