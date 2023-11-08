import boto3

from django_ses import settings


def create_client():
    ses_conn = boto3.client(
        'ses',
        aws_access_key_id=settings.ACCESS_KEY,
        aws_secret_access_key=settings.SECRET_KEY,
        aws_session_token=settings.SESSION_TOKEN,
        region_name=settings.AWS_SES_REGION_NAME,
        endpoint_url=settings.AWS_SES_REGION_ENDPOINT_URL,
        config=settings.AWS_SES_CONFIG,
    )
    return ses_conn


def create_ses_template(template_name, subject, text_part, html_part):
    client = create_client()
    template = {
        'TemplateName': template_name,
        'SubjectPart': subject,
        'HtmlPart': html_part
    }
    if text_part:
        template['TextPart'] = text_part
    response = client.create_template(Template=template)
    return response


def update_ses_template(template_name, subject, text_part, html_part):
    client = create_client()
    template = {
        'TemplateName': template_name,
        'SubjectPart': subject,
        'HtmlPart': html_part
    }
    if text_part:
        template['TextPart'] = text_part
    response = client.update_template(Template=template)
    return response


def delete_ses_template(template_name):
    client = create_client()
    response = client.delete_template(TemplateName=template_name)

    return response


def get_ses_template(template_name):
    client = create_client()
    response = client.get_template(TemplateName=template_name)

    return response


def get_ses_list_template(count):
    client = create_client()
    response = client.get_template(MaxItems=count)

    return response


def send_ses_template_email(from_email, recipients):
    client = create_client()
    response = None
    for recipient in recipients:
        try:
            response = client.send_templated_email(
                Source=from_email,
                Destination={
                    'ToAddresses': [recipient]
                },
                Template='my_template',
                TemplateData='{\"name\":\"Recipient\"}'
            )
        except Exception as e:
            pass
    return response


def send_bulk_ses_template_email(from_email, template_name, emails):
    client = create_client()
    response = client.send_bulk_templated_email(
        Source=from_email,
        Template=template_name,
        DefaultTemplateData='{ "name":"John", "favoriteColor":"green"}',
        Destinations=[
            {
                'Destination': {
                    'ToAddresses': [
                        'recipient1@example.com',
                    ]
                },
                'ReplacementTemplateData': '{ "name":"Jane", "favoriteColor":"blue" }'
            },
            {
                'Destination': {
                    'ToAddresses': [
                        'recipient2@example.com',
                    ]
                }
            }
        ]
    )
    return response