__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

from celery import Celery
import traceback
import logging
import pymongo
from config import MONGODB_URI, CELERY_OPTS, DB_NAME, DATASET_DIR, EXPIRY_SPAN, SCAN_INTERVAL, setup_logging
import time
from crossval.moses_cross_val import CrossValidation
from models.dbmodels import Session
import os
import shutil
import base64
from datetime import timedelta


celery = Celery('mozi_snet', broker=CELERY_OPTS["CELERY_BROKER_URL"])
celery.conf.update(CELERY_OPTS)
setup_logging()




def get_expired_sessions(db, time_span):
    """
    Given a database object reference, it will return all the sessions where the difference between
    their end_time and the current time is greater than or equal to time_span
    :param db: Mongo object
    :param time_span: the time difference in seconds
    :return:
    """

    sessions = Session.get_finished_sessions(db)
    now = time.time()
    if len(sessions) > 0:
        expired_sessions = filter(lambda k: (now - k.end_time) > time_span, sessions)
        return expired_sessions

    return None


@celery.on_after_configure.connect
def setup_periodic_task(sender, **kwargs):
    sender.add_periodic_task(SCAN_INTERVAL, scan_expired_sessions.s(EXPIRY_SPAN), name="Scan for expired sessions")


@celery.task
def start_analysis(**kwargs):
    """
    A celery task that runs the MOSES analysis
    :param session: The session object
    :param cwd: Current working directory to store the results of the analysis
    :param db: A reference to the mongo database
    :return:
    """
    db = pymongo.MongoClient(MONGODB_URI)[DB_NAME]
    logger = logging.getLogger("mozi_snet")

    session = Session(kwargs["id"], kwargs["moses_options"], kwargs["crossval_options"],
                      kwargs["dataset"], kwargs["mnemonic"], kwargs["target_feature"])

    session.save(db)

    session.status = 1
    session.progress = 1
    session.start_time = time.time()
    session.update_session(db)

    try:
        moses_cross_val = CrossValidation(session, db, kwargs["swd"])
        logger.info("Started cross-validation run")
        moses_cross_val.run_folds()
        logger.info("Cross-validation done successfully")
        session.status = 2
        session.message = "Success"
        session.progress = 100
    except Exception as e:
        session.status = -1
        session.message = e.__str__()
        logger.error(f"Task failed with {traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)}")

    finally:
        session.end_time = time.time()
        session.update_session(db)


@celery.task
def scan_expired_sessions(time_span):
    """
    Scans for sessions that are expired. The default time for a session expiry is two weeks.
    The time for expiry can be configured by changing the $EXPIRY_SPAN environment variable
    :param time_span: the time period for a session to expire
    :return:
    """
    db = pymongo.MongoClient(MONGODB_URI)[DB_NAME]
    logger = logging.getLogger("mozi_snet")
    td = timedelta(days=time_span)
    logger.info("Scanning expired sessions")
    result = get_expired_sessions(db, td.total_seconds())

    if result:
        delete_expired_sessions.apply_async(result)


@celery.task
def delete_expired_sessions(sessions):
    """
    Deletes the results and datasets of sessions that have expired.
    :return:
    """
    db = pymongo.MongoClient(MONGODB_URI)[DB_NAME]
    logger = logging.getLogger("mozi_snet")
    try:
        for session in sessions:
            zip_file = os.path.join(DATASET_DIR, f"session_{session.mnemonic}.zip")
            sess_dir = os.path.join(DATASET_DIR, f"session_{session.mnemonic}")

            os.remove(zip_file)
            shutil.rmtree(sess_dir)

            session.expired = True
            session.update_session(db)

        logger.info(f"Successfully deleted {len(sessions)} sessions")

    except Exception as ex:
        logger.error(f"Ran into error f{ex.__str__()}")