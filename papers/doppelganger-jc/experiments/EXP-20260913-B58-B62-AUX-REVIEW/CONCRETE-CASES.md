# Concrete cases from actual outputs

These cases are illustrative selections after the results, not a random sample or an independent validation set. Full paired tables retain all rescues, harms and unresolved cases. Every gold answer below is an author reference.

## 1. B58: A same-fact background edit introduces a new error

Only the background construction/order changes in this pair. The target and background facts are held fixed; the improvement is not universal.

**B58-apertus-N01-C01-BA-AB-DIFFERENT_BA_CD-UA** · C · [Full actual input and output](B58/evidence/apertus-N01-C01.json)

```text

R2：昨天另一处场地发生了一件事。魏景初把叶知岳吓哭了。
R1：操场上的争执已经平息。陶星澄确实把蒋沐衡拉开了。

```

Author roles: `{"actor": "陶星澄", "undergoer": "蒋沐衡"}`

Actual answer:

```text

{"undergoer":"蒋沐衡","actor":"陶星澄"}

```

**B58-apertus-N01-C01-BA-AB-DIFFERENT_BEI_DC-UA** · R · [Full actual input and output](B58/evidence/apertus-N01-C01.json)

```text

R2：昨天另一处场地发生了一件事。叶知岳被魏景初吓哭了。
R1：操场上的争执已经平息。陶星澄确实把蒋沐衡拉开了。

```

Author roles: `{"actor": "陶星澄", "undergoer": "蒋沐衡"}`

Actual answer:

```text

{"undergoer":"陶星澄","actor":"蒋沐衡"}

```

## 2. B59: A counterexample to the predicted OSV harm

The predesignated simple order account predicted harm for this target/schema cell. This is one of its three rescues, alongside one harm.

**B59-apertus-F06-BA-SVO_TOPIC-D_ACTOR-UA** · R · [Full actual input and output](B59/evidence/apertus-F06.json)

```text

R2：昨天另一场活动已经结束。下面逐人说明这一组的互动情况：钟亦辰，已经打伤了孟书涵。
R1：仓库里的救援行动已经结束。杜清妍确实把谢景行救出了。

```

Author roles: `{"actor": "杜清妍", "undergoer": "谢景行"}`

Actual answer:

```text

{"undergoer":"杜清妍","actor":"谢景行"}

```

**B59-apertus-F06-BA-OSV_TOPIC-D_ACTOR-UA** · C · [Full actual input and output](B59/evidence/apertus-F06.json)

```text

R2：昨天另一场活动已经结束。下面逐人说明这一组的互动情况：孟书涵，钟亦辰已经打伤了。
R1：仓库里的救援行动已经结束。杜清妍确实把谢景行救出了。

```

Author roles: `{"actor": "杜清妍", "undergoer": "谢景行"}`

Actual answer:

```text

{"undergoer":"谢景行","actor":"杜清妍"}

```

## 3. B60: The fixed demonstration package can harm Apertus

The target test is held fixed; DEMO_F adds the frozen four demonstrations. Full demonstration text is in the linked record. This package is not a single-factor linguistic manipulation.

**B60-apertus-F07-BEI-BA_TOPIC-C_ACTOR-AU-ZERO** · C · [Full actual input and output](B60/evidence/apertus-F07.json)

```text

R2：昨天另一场活动已经结束。下面逐人说明这一组的互动情况：江明轩，已经把邹念初扶住了。
R1：体育馆门口的拦截已经结束。贺安澜确实被程知远拦下了。

```

Author roles: `{"actor": "程知远", "undergoer": "贺安澜"}`

Actual answer:

```text

{"actor":"程知远","undergoer":"贺安澜"}

```

**B60-apertus-F07-BEI-BA_TOPIC-C_ACTOR-AU-DEMO_F** · OTHER_W · [Full actual input and output](B60/evidence/apertus-F07.json)

```text

R2：昨天另一场活动已经结束。下面逐人说明这一组的互动情况：江明轩，已经把邹念初扶住了。
R1：体育馆门口的拦截已经结束。贺安澜确实被程知远拦下了。

```

Author roles: `{"actor": "程知远", "undergoer": "贺安澜"}`

Actual answer:

```text

{"actor":"江明轩","undergoer":"邹念初"}

```

## 4. B60: The same package can rescue a Qwen error

The target test is held fixed; DEMO_F adds the frozen four demonstrations. Full demonstration text is in the linked record. This package is not a single-factor linguistic manipulation.

**B60-qwen-F07-BEI-BA_TOPIC-C_ACTOR-AU-ZERO** · R · [Full actual input and output](B60/evidence/qwen-F07.json)

```text

R2：昨天另一场活动已经结束。下面逐人说明这一组的互动情况：江明轩，已经把邹念初扶住了。
R1：体育馆门口的拦截已经结束。贺安澜确实被程知远拦下了。

```

Author roles: `{"actor": "程知远", "undergoer": "贺安澜"}`

Actual answer:

```text

{"actor":"贺安澜","undergoer":"程知远"}

```

**B60-qwen-F07-BEI-BA_TOPIC-C_ACTOR-AU-DEMO_F** · C · [Full actual input and output](B60/evidence/qwen-F07.json)

```text

R2：昨天另一场活动已经结束。下面逐人说明这一组的互动情况：江明轩，已经把邹念初扶住了。
R1：体育馆门口的拦截已经结束。贺安澜确实被程知远拦下了。

```

Author roles: `{"actor": "程知远", "undergoer": "贺安澜"}`

Actual answer:

```text

{"actor":"程知远","undergoer":"贺安澜"}

```

## 5. B61: A role reversal without JSON punctuation

The labelled key/value response is format-compliant yet reverses the target roles; role labels and answer order remain part of this interface.

**B61-apertus-F10-BEI-BEI_TOPIC-D_ACTOR-AU-KV** · R · [Full actual input and output](B61/evidence/apertus-F10.json)

```text

R2：昨天另一场活动已经结束。下面逐人说明这一组的互动情况：薛景宁，已经被廖文悦拉住了。
R1：关于活动安排的商谈已经结束。魏书恒确实被蒋安然说服了。

```

Author roles: `{"actor": "蒋安然", "undergoer": "魏书恒"}`

Actual answer:

```text

actor=魏书恒；undergoer=蒋安然

```

## 6. B62: The frozen package rescues a fresh-material reversal

The demonstrations are exactly those used in B60; both orders rescue this new-material case. It is a package-level, same-template transfer result.

**B62-qwen-G02-BEI-AU-BEI_TOPIC-ZERO** · R · [Full actual input and output](B62/evidence/qwen-G02.json)

```text

R2：昨天另一场活动已经结束。下面逐人说明这一组的互动情况：袁知夏，已经被戚书航吓退了。
R1：拥抱练习已经结束。汪承远确实被侯语桐抱住了。

```

Author roles: `{"actor": "侯语桐", "undergoer": "汪承远"}`

Actual answer:

```text

{"actor":"汪承远","undergoer":"侯语桐"}

```

**B62-qwen-G02-BEI-AU-BEI_TOPIC-DEMO_F** · C · [Full actual input and output](B62/evidence/qwen-G02.json)

```text

R2：昨天另一场活动已经结束。下面逐人说明这一组的互动情况：袁知夏，已经被戚书航吓退了。
R1：拥抱练习已经结束。汪承远确实被侯语桐抱住了。

```

Author roles: `{"actor": "侯语桐", "undergoer": "汪承远"}`

Actual answer:

```text

{"actor":"侯语桐","undergoer":"汪承远"}

```

**B62-qwen-G02-BEI-AU-BEI_TOPIC-DEMO_R** · C · [Full actual input and output](B62/evidence/qwen-G02.json)

```text

R2：昨天另一场活动已经结束。下面逐人说明这一组的互动情况：袁知夏，已经被戚书航吓退了。
R1：拥抱练习已经结束。汪承远确实被侯语桐抱住了。

```

Author roles: `{"actor": "侯语桐", "undergoer": "汪承远"}`

Actual answer:

```text

{"actor":"侯语桐","undergoer":"汪承远"}

```
