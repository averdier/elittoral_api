import os
import numpy as np
import cv2
from app import create_celery_app
from app.core.picture_engine import build_thumbnail, open_resource_content, save_result
from app.models import ReconResource, Analysis, AnalysisResult
from app.extensions import db

celery = create_celery_app()


@celery.task
def task_build_thumbnail(resource_id):
    """
    Tache de generation de la vignette
    
    :param resource_id: Resource unique Id
    :type resource_id: int
    """

    resource = ReconResource.query.filter_by(id=resource_id).first()

    if resource is None:
        raise ValueError('Resource #' + str(resource_id) + ' not found')

    build_thumbnail(resource)


@celery.task
def new_analysis(analysis_id):
    """
    Run a analysis

    :param analysis_id: Analysis unique id
    :type analysis_id: int
    """

    analysis = Analysis.get_from_id(analysis_id)

    if analysis is None:
        raise Exception('Analysis #' + str(analysis_id) + ' not found')

    if analysis.minuend_recon is None:
        raise Exception('Analysis minuend recon is required')
    if analysis.subtrahend_recon is None:
        raise Exception('Analysis subtrahend recon is required')

    analysis.state = 'progress'
    analysis.total = 0
    analysis.current = 0
    analysis.result = 0

    tasks = []
    for minuend in analysis.minuend_recon.resources.all():
        subthrahend = analysis.subtrahend_recon.resources.filter_by(number=minuend.number).first()

        if subthrahend is not None:
            if minuend.filename is not None and subthrahend.filename is not None:
                tasks.append({'minuend': minuend, 'subthrahend': subthrahend})

    analysis.total = len(tasks)
    if analysis.total > 0:
        try:
            # Create vars before loop for less memory consumption
            diminuend_img = open_resource_content(tasks[0]['minuend'])
            subtrahend_img = open_resource_content(tasks[0]['subthrahend'])
            substractor = cv2.createBackgroundSubtractorMOG2()
            result_img = None

            for i in range(0, len(tasks)):

                minuend = tasks[i]['minuend']
                subthrahend = tasks[i]['subthrahend']
                if i > 0:
                    diminuend_img = open_resource_content(minuend)
                    subtrahend_img = open_resource_content(subthrahend)

                substractor.apply(diminuend_img)
                result_img = substractor.apply(subtrahend_img)

                diff = cv2.countNonZero(result_img)
                total = diminuend_img.shape[0] * diminuend_img.shape[1]
                result = diff * 100 / total

                filename = save_result(minuend, subthrahend, result_img)
                a_result = AnalysisResult(
                    analysis=analysis,
                    minuend_resource=minuend,
                    subtrahend_resource=subthrahend,
                    filename=filename,
                    result=result
                )
                analysis.current += 1
                analysis.result += result

                db.session.add(analysis)
                db.session.add(a_result)
                db.session.commit()

                # Reset
                substractor = cv2.createBackgroundSubtractorMOG2()
            analysis.state = 'complete'

        except Exception as e:
            analysis.state = 'error'
            analysis.message = str(e)

        finally:
            db.session.add(analysis)
            db.session.commit()
    else:
        analysis.state = 'error'
        analysis.message = 'No valid resources found'

        db.session.add(analysis)
        db.session.commit()