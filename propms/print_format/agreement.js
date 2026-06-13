{/* <style>
    body {
        font-family: "Segoe UI", Arial, sans-serif;
        margin: 40px;
        line-height: 1.7;
        color: #2c3e50;
    }

    .welcome-header {
        text-align: center;
        margin-bottom: 30px;
        border-bottom: 3px solid #3498db;
        padding-bottom: 15px;
    }

    .welcome-header h1 {
        color: #1a5276;
        margin: 0;
        font-size: 30px;
    }

    .welcome-header p {
        color: #555;
        margin-top: 5px;
        font-size: 16px;
    }

    .welcome-body {
        margin-top: 25px;
        font-size: 15px;
        color: #34495e;
    }

    .info-list {
        margin: 20px 0;
        padding: 0;
        list-style: none;
        font-size: 15px;
    }

    .info-list li {
        margin: 10px 0;
        padding: 8px 12px;
        border-left: 4px solid #3498db;
        background: #f8faff;
        border-radius: 4px;
    }

    .footer-note {
        margin-top: 50px;
        font-size: 13px;
        color: #555;
        text-align: center;
        border-top: 1px dashed #bbb;
        padding-top: 15px;
    }
</style>

<div class="welcome-header">
    <h1>Welcome to {{ doc.property }}</h1>
    <p>We’re delighted to have you with us 🎉</p>
</div>

<div class="welcome-body">
    <p>Dear <b>{{ doc.lease_customer }}</b>,</p>

    <p>
        Thank you for choosing us. Below are the details of your agreement:
    </p>

    <ul class="info-list">
        <li><b>Room:</b> {{ doc.room }}</li>
        <li><b>Start Date:</b> {{ frappe.utils.formatdate(doc.start_date) }}</li>
        <li><b>Term Type:</b> {{ doc.term_type }}</li>
        {% if doc.term_type == "Fixed-term" %}
            <li><b>End Date:</b>
                {% if doc.end_date %}
                    {{ frappe.utils.formatdate(doc.end_date) }}
                {% else %}
                    Not Provided
                {% endif %}
            </li>
        {% endif %}
        <li><b>Billing Period:</b> {{ doc.frequency }}</li>
        <li><b>Fee Amount:</b> {{ frappe.format_value(doc.fee_amount, {"fieldtype":"Currency"}) }}</li>
        <li><b>Security Deposit:</b> {{ frappe.format_value(doc.security_deposit, {"fieldtype":"Currency"}) }}</li>
        <li><b>Security Status:</b> {{ doc.security_status }}</li>
    </ul>

    <p>
        Please take a moment to go through our <b>House Rules</b>, which were shared with you during move-in.
        If you have any questions, our property manager will be happy to assist.
    </p>

    <p><i>We wish you a comfortable and pleasant stay!</i></p>
</div>

<div class="footer-note">
    Generated on {{ frappe.utils.formatdate(frappe.utils.now_datetime()) }}
</div> */}
