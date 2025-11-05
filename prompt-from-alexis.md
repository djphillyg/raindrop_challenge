# Context Free Grammars + Eval Toy

https://cookbook.openai.com/examples/gpt-5/gpt-5_new_params_and_tools#3-contextfree-grammar-cfg

<aside>
✨

GPT-5 has newly added support for Context Free Grammars (CFG). This allows you to constrain the model’s output in a way in a much more powerful way. You’ll create a small app for experimenting with CFG’s + a few evals for proving it works!

</aside>

### Timeline:

Estimated Commitment: 6.5 hours

Requested Delivery: 3 days

### Deliverables

*Please send deliverables within 3 days of starting project! If you have scheduling conflicts that prevent this (or disagree with our timeline!), just let us know before starting.*

- A deployed app where someone can type in a natural language query “sum the total of all orders placed in the last 30 hours” and see data from clickhouse returned.
    - You don’t need to render graphs/tables/etc. Raw JSON response is fine!
    - You must use GPT-5’s newly added Context Free Grammar
- 3+ Evals for the generation of the CFG. You can roll your own eval framework, or use anything off the shelf. Don’t overthink this!
    - The evals can be run from the app you deploy, a script, etc.
- GitHub + source code!

### Getting Started

- Use [Tinybird](http://tinybird.com) or [ClickHouse Cloud](http://clickhouse.cloud) to ingest some CSV data. Choose any large, 1000+ row dataset you’d like.
- Define a CFG for the ClickHouse table.
- The app you make should have a prompt for typing in any query, and seeing the response that is returned from the API.
- Make sure to also make just a few (3 is okay!) evals.




<prompt>
# Context Free Grammars + Eval Toy

https://cookbook.openai.com/examples/gpt-5/gpt-5_new_params_and_tools#3-contextfree-grammar-cfg

<aside>
✨

GPT-5 has newly added support for Context Free Grammars (CFG). This allows you to constrain the model’s output in a way in a much more powerful way. You’ll create a small app for experimenting with CFG’s + a few evals for proving it works!

</aside>

### Timeline:

Estimated Commitment: 6.5 hours

Requested Delivery: 3 days

### Deliverables

*Please send deliverables within 3 days of starting project! If you have scheduling conflicts that prevent this (or disagree with our timeline!), just let us know before starting.*

- A deployed app where someone can type in a natural language query “sum the total of all orders placed in the last 30 hours” and see data from clickhouse returned.
    - You don’t need to render graphs/tables/etc. Raw JSON response is fine!
    - You must use GPT-5’s newly added Context Free Grammar
- 3+ Evals for the generation of the CFG. You can roll your own eval framework, or use anything off the shelf. Don’t overthink this!
    - The evals can be run from the app you deploy, a script, etc.
- GitHub + source code!

### Getting Started

- Use [Tinybird](http://tinybird.com) or [ClickHouse Cloud](http://clickhouse.cloud) to ingest some CSV data. Choose any large, 1000+ row dataset you’d like.
- Define a CFG for the ClickHouse table.
- The app you make should have a prompt for typing in any query, and seeing the response that is returned from the API.
- Make sure to also make just a few (3 is okay!) evals.
</prompt>


<guidelines>
- focus on 0-1 generation
- i do not have context into context free grammars and how to implement them with sql, so i need to learn it first
- backend in python, frontend in next.js
- tinybird will be the datastore
- focus on the easiest way to create an eval framework
- build out a full plan for me to execute on this
- create a design and implementation plan in markdown to execute on in this directory
</guidelines>
