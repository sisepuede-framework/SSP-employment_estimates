Part of the possible [[Impact channels]] of MINDSET.
### Description

Exogenous impacts are one of the main policy levers in MINDSET. Exogenous impacts (at the moment) can be investments or final demand changes. Exogenous impacts are collected and calculated through the `exog_vars.py` and `scenario.py`.

#### Exogenous investment (by sector!)
*Note: as the model does not currently have **investment by sector** baseline values, right now exogenous investment can only be specified with a dollar (absolute) value.*

Exogenous investment, by investing sector basically takes the values given to it in the scenario files and translates these into FCF final demand using the investment converter. The investment converter currently is *global* and located at `GLORIA_template\\Investment\\Inv_conversion.csv`
#### Exogenous final demand
Exogenous final demand is collected from the scenario files. If specified not in absolute terms, then the current (initial) y0 is used to calculate its value.

### Flows


```mermaid
	flowchart LR

	Scenario:::hl --> INV_model --> INV_converter
	INV_converter:::file --> dy_inv_exog:::outcome 
	dy_inv_exog --> IO_model --> dq_inv_exog:::outcome

	Scenario --> dy_hh_exog_fd:::outcome --> IO_model
	Scenario --> dy_gov_exog_fd:::outcome --> IO_model
	Scenario --> dy_fcf_exog_fd:::outcome --> IO_model

	IO_model --> dq_hh_exog_fd:::outcome
	IO_model --> dq_gov_exog_fd:::outcome
	IO_model --> dq_fcf_exog_fd:::outcome

	classDef freevar fill:#82C0CC
	classDef file fill:#4B6858,color:white
	classDef outcome fill:#E94F37,color:white
	classDef hl stroke:#FFA62B,stroke-width:4px
```

## Notes

