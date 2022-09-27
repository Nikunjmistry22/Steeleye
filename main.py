

import pandas as pd

import boto3

import xml.etree.cElementTree as et
import requests
from io import BytesIO


session = boto3.Session(
    aws_access_key_id="xxxxxxxxxxxxxx", aws_secret_access_key="xxxxxxxxxxxxxxxxxxxxx"
)
s3 = session.resource("s3")

def upload_to_aws(local_file, aws_file):
    s3.Bucket("steeleye-assignment").upload_file(local_file, aws_file)


def get_root_from_xml(xml_file):

    # Parse XML file

    tree = et.parse(xml_file)
    root = tree.getroot()
    return root


def get_download_link_from_xml(xml_file):

    root = get_root_from_xml(xml_file)
    download_link = ""
    for link in root.iter("response"):
        for doc in link.iter("str"):
            if doc.attrib["name"] == "download_link":
                download_link = doc.text
                break
    return download_link


def download_and_extract_file_from_url(download_link):

    filename = download_link.split("/")[-1]
    print("Downloading Started")

    req = requests.get(download_link)
    print("Downloading Completed")

    zipfile = zipfile.ZipFile(BytesIO(req.content))
    zipfile.extractall(".")
    return filename


def get_data_from_xml(filename):
    root = get_root_from_xml(filename.split(".")[0])


    Id = []
    FullNm = []
    ClssfctnTp = []
    CmmdtyDerivInd = []
    NtnlCcy = []
    Issrs = []

    # Namespace to be added at the start of every element (xmlns)

    namespace = "{urn:iso:std:iso:20022:tech:xsd:auth.036.001.02}"

    # Iterating all elements with Tag 'FinInstrmGnlAttrbts'

    for FinInstrmGnlAttrbts in root.iter("{0}FinInstrmGnlAttrbts".format(namespace)):
        Id.append(
            FinInstrmGnlAttrbts.find("{0}Id".format(namespace)).text
        )  # Getting Id from the Id Tag
        FullNm.append(
            FinInstrmGnlAttrbts.find("{0}FullNm".format(namespace)).text
        )  # Getting FullNm from the FullNm Tag
        ClssfctnTp.append(
            FinInstrmGnlAttrbts.find("{0}ClssfctnTp".format(namespace)).text
        )  # Getting ClssfctnTp from the ClssfctnTp Tag
        CmmdtyDerivInd.append(
            FinInstrmGnlAttrbts.find("{0}CmmdtyDerivInd".format(namespace)).text
        )  # Getting CmmdtyDerivInd from the CmmdtyDerivInd Tag
        NtnlCcy.append(
            FinInstrmGnlAttrbts.find("{0}NtnlCcy".format(namespace)).text
        )  # Getting NtnlCcy from the NtnlCcy Tag

    for Issr in root.iter("{0}Issr".format(namespace)):
        Issrs.append(Issr.text)

    # Save all the data in CSV

    convert_to_csv(Id, FullNm, ClssfctnTp, CmmdtyDerivInd, NtnlCcy, Issrs)


def convert_to_csv(Id, FullNm, ClssfctnTp, CmmdtyDerivInd, NtnlCcy, Issrs):
    df = pd.DataFrame(
        {
            "Id": Id,
            "FullNm": FullNm,
            "ClssfctnTp": ClssfctnTp,
            "CmmdtyDerivInd": CmmdtyDerivInd,
            "NtnlCcy": NtnlCcy,
            "Issr": Issrs,
        }
    )
    df.to_csv("Final.csv")
    print("CSV created succesfully with name 'Final.csv'")


if __name__ == "main":
    xml_file = "select.xml"

    # Getting download link from the xml file.

    download_link = get_download_link_from_xml(xml_file)

    # Downloading and extracting file from the URL.

    filename = download_and_extract_file_from_url(download_link)

    # Finally parsing required data from downloaded xml and saving it to a csv

    get_data_from_xml(filename)
