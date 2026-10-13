# Week 4 observation.md

## Task 1

### Why can a Bloom filter never have a false negative? One sentence, structural
존재하는 원소에 대해 해시값에 해당하는 비트를 1로 바꾸고, 이후에 다시 0으로 바꾸지 않기 때문에 흔적이 지워지지 않아 False Negative가 발생하지 않는다.

### Your predicted and measured false-positive rates. If they differ, say why
예상 0.860% / 측정 0.835% 
예상값은 완전 균등한 해시를 가정한 값이지만 측정은 유한한 표본으로 실험한 측정값이므로 값의 차이가 발생했다.

### Which combining rule you used for Flajolet-Martin, and what the others gave you
측정값을 그룹으로 나누고, 각 그룹별 평균의 중앙값을 사용하여 실제의 1.17배를 얻었고, 단순 평균은 2.51배, 중앙값은 1.23배였다.

### Reservoir sampling holds k items but has to be correct for a stream whose length it never learns. Where in your code does that actually happen?

`j = rng.randrange(i + 1)`에서 `j < k`일 때 표본을 교체하고
최종 포함 확률은 각 항목마다 k/n이며 최대 k개만 저장한다.

## Task 2

### The size where exact became unbearable, and whether time or memory gave out first
30초 안에 1,024만 개를 처리하는 것을 목표로 했고, 980만 개를 처리하는데 30초를 넘겨서 중단했다. 

### The two growth rates from A4
입력이 1만개에서 64만 개로 64배 증가할 때 set 메모리는 0.314→20.540MB로 약 65.48배 증가했다. -> O(n)
FM은 7,588→7,594바이트로 거의 일정했다 -> O(1)

### Is a factor of two good enough for "how many distinct users visited today"? Give a case where it is and a case where it is not
방문자 규모나 대략적인 추세를 파악하는 것에는 충분하지만 방문자 수에 따라 광고요금을 청구한다거나 하는 경우에는 부족하다.

### Report FM's accuracy ratio at each size. Does it get better or worse as n grows?
1만, 4만, 16만, 64만 개에서 추정/실제 비율은 1.495, 1.040, 1.648, 1.446이었다.
입력이 커져도 오차가 항상 줄어들지는 않았다.

### State your machine: CPU, RAM, what else was running
사용 랩탑 = 갤럭시북 5프로 Ultra 5 226V, RAM 16GB
WSL 가상환경과 VS Code, ChatGPT 앱 (Codex)을 사용하였다.

## Task 3

### Which parameter you changed and the value you chose, with the derivation
해시 개수를 1개에서 7개로 늘렸다. 
오탐률을 최소화하는 k*=(m/n)ln(2)는 10비트/항목에서 약 6.93이다.

### R6: the floor for 10 bits per item, and how close you got
항목당 10비트인 Bloom Filter의 이론적 최적값은 0.819%이며 실측값은 0.894%로 근접했다.

### What you would do if n were unknown
n 값을 너무 작게 예상하면 필터가 포화되어 오탐이 늘고 너무 크게 예상하면 메모리가 낭비되므로 필요에 따라 필터를 확장 가능한 Bloom Filter를 사용한다.
