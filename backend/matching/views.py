from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from jobs.models import Offre
from .models import ResultatMatching
from .nlp_matcher import (extraire_texte_cv, extraire_competences,
                           calculer_score, clustering_offres)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def lancer_matching(request):
    user = request.user

    if not user.cv_file:
        return Response({'error': 'Veuillez uploader votre CV'}, status=400)

    # ── Extraire texte CV ──
    cv_texte = extraire_texte_cv(user.cv_file.path)
    cv_competences = extraire_competences(cv_texte)

    user.competences = cv_competences
    user.save()

    # ── Calculer scores ──
    offres = Offre.objects.all()
    resultats = []

    for offre in offres:
        scores = calculer_score(
            cv_texte=cv_texte,
            offre_description=offre.description,
            cv_competences=cv_competences,
            offre_competences=offre.competences_requises,
            cv_experience=user.experience_annees,
            offre_experience=offre.experience_requise,
            cv_localisation=user.localisation,
            offre_localisation=offre.localisation,
        )

        ResultatMatching.objects.update_or_create(
            utilisateur=user,
            offre=offre,
            defaults={
                'score_total': scores['score_total'],
                'score_cosinus': scores['score_cosinus'],
                'score_jaccard': scores['score_jaccard'],
                'score_experience': scores['score_experience'],
                'score_geo': scores['score_geo'],
            }
        )

        resultats.append({
            'offre_id': offre.id,
            'titre': offre.titre,
            'entreprise': offre.entreprise,
            'localisation': offre.localisation,
            'type_contrat': offre.type_contrat,
            'url': offre.url_source,
            **scores
        })

    resultats.sort(key=lambda x: x['score_total'], reverse=True)

    # ── Clustering ──
    descriptions = [o.description for o in offres]
    clusters = clustering_offres(descriptions)

    return Response({
        'competences_cv': cv_competences,
        'total_offres': len(resultats),
        'resultats': resultats,
        'clusters': clusters
    })