NCPT = [
    ['ncpt_ar', 'NCPT Arithmetic Reasoning', 'data'],
    ['ncpt_dsc', 'NCPT Digit Symbol Coding', 'data'],
    ['ncpt_sb', 'NCPT Scale Balance', 'data'],
    ['ncpt_gr', 'NCPT Grammatical Reasoning', 'data'],
    ['ncpt_ms', 'NCPT Memory Span', 'data'],
    ['ncpt_or', 'NCPT Object Recognition', 'data'],
    ['ncpt_rms', 'NCPT Reverse Memory Span', 'data'],
    ['ncpt_tma', 'NCPT Trail Making A', 'data'],
    ['ncpt_tmb', 'NCPT Trail Making B', 'data'],
]

def visit(ncpt=False):
    return [
        ['s', 'Schedule', 'event'],
        ['ar', 'Alertness Questionnaire'],
        ['erb', 'Empty Room (before)', 'data'],
        ['rs', 'Resting State', 'data'],
        ['erf', 'ERF', 'data'],
        ['cg', 'Complete Game', 'data'],
        ['og', 'Observe Game', 'data'],
    ] + (NCPT if ncpt else []) + [
        ['era', 'Empty Room (after)', 'data'],
        ['pay', 'Pay Subject', 'payment'],
        ['notes', 'Notes'],
    ]

tasks = {
    ('screening', 'Screening'): [
        ['oc', 'Obtain Consent'],
        ['sq', 'Screening Questionnaire'],
        ['el', 'Eligible?'],
        ['nda', 'NDA'],
    ],
    ('baseline', 'Baseline Visit'): [
        ['ic', 'Informed Consent', 'attachment'],
        ['w9', 'W9'],
        ['dq', 'Demographics Questionnaire'],
        ['erb', 'Empty Room (before)', 'data'],
        ['rs', 'Resting State', 'data'],
        ['erf', 'ERF', 'data'],
    ] + NCPT + [
        ['era', 'Empty Room (after)', 'data'],
        ['s', 'Schedule Training Visits 1-5'],
        ['pay', 'Pay Subject', 'payment']
    ],
    ('bt1', 'Brain Training 1'): visit(),
    ('bt2', 'Brain Training 2'): visit(),
    ('bt3', 'Brain Training 3'): visit(),
    ('bt4', 'Brain Training 4'): visit(),
    ('bt5', 'Brain Training 5'): visit(True),
}

records = []
section_num = 0
task_num = 0
for section, section_tasks in tasks.items():
    section_num += 1
    task_num = 0
    section_id, section_name = section
    for task in section_tasks:
        task_num += 1
        task_type = None
        if len(task) == 3:
            task_id, task_name, task_type = task
        else:
            task_id, task_name = task
        
        records.append("""<record model="naas.experiment.task" id="KER2020_1_{}_{}">
        <field name="experiment_id" ref="KER2020_1" />
        <field name="group">{}. {}</field>
        <field name="name">{}.{}{} {}</field>{}
    </record>

    """.format(
            section_id,
            task_id,
            section_num,
            section_name,
            section_num,
            '0' if task_num < 10 else '',
            task_num,
            task_name,
            '\n        <field name="task_type">{}</field>'.format(task_type) if task_type is not None else ''
        ))


final = """<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record model="naas.experiment" id="KER2020_1">
        <field name="name">KER2020.1</field>
    </record>

    {}
</odoo>""".format("".join(records))

open('main.xml', 'w').write(final)