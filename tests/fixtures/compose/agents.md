# AGENTS

## Constitutional Invariants

{% for inv_id, inv in invariants.items() %}
### {{ inv_id }}

{{ inv.claim }}

Witness: {% for w in inv.structural_witness %}{{ w }}{% if not loop.last %}, {% endif %}{% endfor %}

{% endfor %}
