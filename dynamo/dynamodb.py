import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
from datetime import datetime
import time
import uuid
from decimal import Decimal
from pprint import pprint
from botocore.exceptions import ClientError

# There is some weird stuff in DynamoDB JSON responses. These utils work better.
# I am not using  in this example.
# from dynamodb_json import json_util as jsond

# There are a couple of types of client.
# I create both because I like operations from both of them.
#
# I comment out the key information because I am getting this from
# my ~/.aws/credentials files. Normally this comes from a secrets vault
# or the environment.
#
# dynamodb = boto3.resource('dynamodb',
#                           # aws_access_key_id=aws_access_key_id,
#                           # aws_secret_access_key=aws_secret_access_key,
#                           region_name='us-east-1')
dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id= "AKIA4I37LAIQNHRFY55F",
                          aws_secret_access_key= "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",
                          region_name='us-east-2')
other_client = boto3.client("dynamodb",
                          region_name='us-east-2')


def get_item(table_name, key_value):
    table = dynamodb.Table(table_name)

    response = table.get_item(
        Key=key_value
    )

    response = response.get('Item', None)
    return response


def do_a_scan(table_name, filter_expression=None, expression_attributes=None, projection_expression=None,
              expression_attribute_names=None):

    table = dynamodb.Table(table_name)

    if filter_expression is not None and projection_expression is not None:
        if expression_attribute_names is not None:
            response = table.scan(
                FilterExpression=filter_expression,
                ExpressionAttributeValues=expression_attributes,
                ProjectionAttributes=projection_expression,
                ExpressionAttributeNames=expression_attribute_names
            )
        else:
            response = table.scan(
                FilterExpression=filter_expression,
                ExpressionAttributeValues=expression_attributes,
                ProjectionAttributes=projection_expression)
    elif filter_expression is not None:
        if expression_attribute_names is not None:
            response = table.scan(
                FilterExpression=filter_expression,
                ExpressionAttributeValues=expression_attributes,
                ExpressionAttributeNames=expression_attribute_names
            )
        else:
            response = table.scan(
                FilterExpression=filter_expression,
                ExpressionAttributeValues=expression_attributes
            )
    elif projection_expression is not None:
        if expression_attribute_names is not None:
            response = table.scan(
                ProjectionExpression=projection_expression,
                ExpressionAttributeNames=expression_attribute_names
            )
        else:
            response = table.scan(
                ProjectionExpression=projection_expression
            )
    else:
        response = table.scan()

    return response["Items"]


def put_item(table_name, item):

    table = dynamodb.Table(table_name)
    res = table.put_item(Item=item)
    return res


def add_message(table_name, inbox_id, sender, message):
    table = dynamodb.Table(table_name)
    Key={
        "inbox_id": inbox_id
    }
    dt = time.time()
    dts = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(dt))

    full_rsp = {
        "timestamp": dts,
        "msg": message,
        "sender": sender,
        "msgId": str(uuid.uuid4())
    }
    UpdateExpression="SET messages = list_append(messages, :i)"
    ExpressionAttributeValues={
        ':i': [full_rsp]
    }
    ReturnValues="UPDATED_NEW"

    res = table.update_item(
        Key=Key,
        UpdateExpression=UpdateExpression,
        ExpressionAttributeValues=ExpressionAttributeValues,
        ReturnValues=ReturnValues
    )

    return res

#how to do filter expressions
def find_by_template(table_name, template):
    print('template:  ', template)
    print('template.items:  ', template.items)


    fe = ' AND '.join(['{0}=:{0}'.format(k) for k, v in template.items()])
    ea = {':{}'.format(k):v for k, v in template.items()}

    tbl = dynamodb.Table(table_name)
    result = tbl.scan(
        FilterExpression=fe,
        ExpressionAttributeValues=ea
    )
    return result

def find_by_template_new(table_name, template):
    print('template:  ', template)
    print('template.items:  ', template.items)


    fe = ' AND '.join(['{0}=:{0}'.format(k) for k, v in template.items()])
    ea = {':{}'.format(k):v for k, v in template.items()}

    tbl = dynamodb.Table(table_name)
    result = tbl.scan(
        FilterExpression=fe,
        ExpressionAttributeValues=ea
    )
    return result


def add_comment(email, comment, tags):
    dt = time.time()
    dts = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(dt))

    item = {
        "comment_id": str(uuid.uuid4()),
        "version_id": str(uuid.uuid4()),
        "email": email,
        "comment": comment,
        "tags": tags,
        "datetime": dts,
        "responses": []
    }

    res = put_item("user_message", item=item)

    return res


def find_by_tag(tag):
    table = dynamodb.Table("user_message")

    expressionAttributes = dict()
    expressionAttributes[":tvalue"] = tag
    filterExpression = "contains(tags, :tvalue)"

    result = table.scan(FilterExpression=filterExpression,
                        ExpressionAttributeValues=expressionAttributes)
    return result


# def write_comment_if_not_changed(new_comment, old_comment):
#
#     new_version_id = str(uuid.uuid4()) #generate a uuid
#     new_comment["version_id"] = new_version_id
#
#     old_version_id = old_comment["version_id"]
#
#     table = dynamodb.Table("comments")
#
#     res = table.put_item(
#         Item=new_comment,
#         ConditionExpression="version_id=:old_version_id",
#         ExpressionAttributeValues={":old_version_id": old_version_id}
#     )
#
#     return res
def write_comment_if_not_changed(new_comment, old_comment):

    new_version_id = str(uuid.uuid4()) #generate a uuid
    new_comment["version_id"] = new_version_id

    old_version_id = old_comment["version_id"]

    table = dynamodb.Table("user_message")

    res = table.put_item(
        Item=new_comment,
        ConditionExpression="version_id=:old_version_id",
        ExpressionAttributeValues={":old_version_id": old_version_id}
    )

    return res

def delete_item_by_key (table_name, title, year, rating, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',
                                  aws_access_key_id="AKIA4I37LAIQNHRFY55F",
                                  aws_secret_access_key="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",
                                  region_name='us-east-2')

    table = dynamodb.Table(table_name)

    try:
        response = table.delete_item(
            Key={
                'year': year,
                'title': title
            }
            # ConditionExpression="info.rating <= :val",
            # ExpressionAttributeValues={
            #     ":val": Decimal(rating)
            # }
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            print(e.response['Error']['Message'])
        else:
            raise
    else:
        return response

def delete_by_key (table_name, key_name, key_value):
    # if not dynamodb:
    #     dynamodb = boto3.resource('dynamodb',
    #                               aws_access_key_id="AKIA4I37LAIQNHRFY55F",
    #                               aws_secret_access_key="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",
    #                               region_name='us-east-2')

    table = dynamodb.Table(table_name)

    try:
        response = table.delete_item(
            Key={
                key_name: key_value
            }
            # ConditionExpression="info.rating <= :val",
            # ExpressionAttributeValues={
            #     ":val": Decimal(rating)
            # }
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            print(e.response['Error']['Message'])
        else:
            raise
    else:
        print('else response: ', response)
        return response

if __name__ == '__main__':
    print("Attempting a conditional delete...")
    delete_response = delete_by_key("inbox", 'inboxId', 1)
    if delete_response:
        print("Delete movie succeeded:")
        pprint(delete_response, sort_dicts=False)


"""

/comments?email=welleynep6@bbc.co.uk

/api/comments?tags=science,math

update expression set balance=balance+50


POST /comments/1234/responses
GET /comments/1234/responses



"""





