from app import build_question_options


def test_build_question_options_includes_correct_answer():
    pool = [
        'Who would survive longest in prison?',
        'Who would be the best spy?',
        'Who would survive a zombie apocalypse?',
        'Who would make the best captain?',
        'Who would win a fight in the dark?',
        'Who would be the best liar?',
        'Who would ruin a road trip?',
        'Who would be best at hide and seek?',
        'Who would become a millionaire fastest?',
        'Who would win a cooking contest?',
        'Who would be the most dramatic?',
    ]

    options = build_question_options(pool, 'Who would win a cooking contest?')

    assert len(options) == 10
    assert 'Who would win a cooking contest?' in options
    assert len(set(options)) == len(options)
