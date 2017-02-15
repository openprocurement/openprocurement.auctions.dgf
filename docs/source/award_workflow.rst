.. _award_workflow: 

Award Workflow
==============

For a more detailed information see :ref:`award`

    * :ref:`Qualification`
    * :ref:`Confirming_qualification`
    * :ref:`Candidate_disqualification`
    * :ref:`Waiting_refusal`


.. graphviz::

    digraph G {
        subgraph cluster_0 {
            label = "award #2";
            node [style=filled];
            edge[style=dashed];
		"pending.waiting" -> cancel;
            color=blue
	}
	subgraph cluster_1 {
		node [style=filled];
            edge[label=" 3d"];
            "pending.verification" -> unsuccessful;
            edge[label="5d**"];
            active -> unsuccessful;
            edge[label=" 3d*"];
		"pending.verification" -> "pending.payment";
            edge[label="*" style=dashed];
            "pending.verification" -> "pending.payment"
		label = "award #1";
		color=blue
	}
            edge[style=dashed];
            active -> unsuccessful;
            edge[label="***"];
	    "pending.waiting" -> "pending.verification";
            edge[label="7d" style=solid];
            "pending.payment" -> unsuccessful;
            edge[label="*" style=dashed];
            "pending.verification" -> unsuccessful;
            edge[style=dashed];
            "pending.payment" -> active;
    }
