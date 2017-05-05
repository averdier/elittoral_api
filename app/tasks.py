from app import create_celery_app
from app.core.picture_engine import build_thumbnail, resource_subtraction
from app.models import Resource, Analysis, AnalysisResult
from app.extensions import db

celery = create_celery_app()


@celery.task
def task_build_thumbnail(resource_id):
    """
    Tache de generation de la vignette
    
    :param resource_id: Resource unique Id
    :type resource_id: int
    """

    resource = Resource.query.filter_by(id=resource_id).first()

    if resource is None:
        raise ValueError('Resource #' + str(resource_id) + ' not found')

    build_thumbnail(resource)


@celery.task
def run_analysis(analysis_id):
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

    # Count total to do
    for resource in analysis.minuend_recon.resources.all():
        if analysis.subtrahend_recon.resources.filter_by(number=resource.number).first() is not None:
            analysis.total += 1

    try:
        for minuend in analysis.minuend_recon.resources.all():
            substrahend = analysis.subtrahend_recon.resources.filter_by(number=minuend.number).first()

            if substrahend is not None:
                result_filename = resource_subtraction(minuend, substrahend)

                result = AnalysisResult(
                    analysis=analysis,
                    minuend_resource=minuend,
                    subtrahend_resource=substrahend,
                    filename=result_filename
                )
                analysis.current += 1

                db.session.add(analysis)
                db.session.add(result)
                db.session.commit()

        analysis.state = 'complete'

    except Exception as e:
        analysis.state = 'error'
        analysis.message = str(e)

    finally:
        db.session.add(analysis)
        db.session.commit()
