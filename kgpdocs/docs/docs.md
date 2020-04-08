






### Execution Environments

Every invocation of a KGPL function entails a small
custom set of KG entities that describe the **execution
environment**.  These values can be used by a function to
control output depending on the execution environment.

For example, the same code might be runnable either on a laptop with a
large screen, or in voice mode.  If the system returns a table, it
might make sense to present the entire result on a scrollable laptop
screen, but in a voice setting it would only make sense to read the
first tuple aloud.  How can this be implemented?

    RenderTable(t: __Table__): __Table__ {
      if (__Environment__.isVoiceOnly) {
        return t[0]
      } else {
        return t
      }
    }

The conditional statement overall always has a precondition
probability of 1.  One particular branch has a precondition
probability that depends on whether its tested condition is true (or,
for the else branch, (1-p)).

### Managing Uncertainty Thresholds

In some cases, the precondition probability is useful for comparing
different alternatives.  The user might have invoked `Compare(x, y)`;
depending on the values for `x` and `y`, either `Compare(x: Person,
y:Person)` or `Compare(x: TimeSeries, y: TimeSeries)` might be more
probable.

But what should be done when the precondition probability of the
maximally-probable option is still quite low?  The right course of
action depends on the environment and context. For example, the
unambiguous interface probably should always run whatever the user
asks for, while the implicit invocation interface should probably only
run code when the confidence is above a certain threshold.

Each invocation interface can register two special values: the minimum
probability for function execution, and the minimum probability for
warning the user prior to function execution.

Finally, there is the probability associated with conditionals.  The
__True__ branch is always evaluated when its probability is 95% or
higher.





- __Run Once, Debug Everywhere__: It is easy to share, examine,
  discuss, copy, and modify single executions.
- __The Universal Class Library__: KGPL offers a class library of more
  than __70 million__ individual and easily-understood types. These
  types reflect real-world categories, such as Presidents, Buildings,
  Emotions, Satellites, and many more
- __Easy Fine-Grained Code Sharing__: KGPL makes it easy to share
  even individual variables with other programs.
- __Practical Python__: Despite all of the above features, KGPL looks and
  feels like Python 99% of the time

