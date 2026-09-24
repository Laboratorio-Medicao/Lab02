import pytest

from experiment.analysis.rank_sum import rank_sum_test


def test_all_values_equal_is_not_applicable():
    result = rank_sum_test([100.0] * 9, [100.0] * 9, alternative="greater")
    assert not result.applicable
    assert result.p_one_sided is None


def test_complete_separation_3x3_exact():
    result = rank_sum_test([1.0, 2.0, 3.0], [4.0, 5.0, 6.0], alternative="less")
    assert result.method == "exato"
    # 1 / C(6, 3)
    assert result.p_one_sided == pytest.approx(0.05)


def test_ties_between_samples_use_permutation():
    # Empate só entre as amostras (o 2): "exact" daria 0,10 / 0,20, sem corrigir empates.
    result = rank_sum_test([1.0, 2.0, 2.0], [2.0, 5.0, 6.0], alternative="less")
    assert result.method.startswith("permutação")
    assert result.p_one_sided == pytest.approx(0.15)
    assert result.p_two_sided == pytest.approx(0.30)


def test_ties_with_large_samples_are_deterministic():
    # 9×9 com empates: C(18, 9) partições, mais que as reamostragens padrão do scipy.
    with_ai = [4, 8, 6, 10, 4, 5, 5, 7, 5]
    without_ai = [14, 4, 8, 4, 9, 7, 8, 11, 5]
    first = rank_sum_test(with_ai, without_ai, alternative="two-sided")
    second = rank_sum_test(with_ai, without_ai, alternative="two-sided")
    assert first.p_two_sided == second.p_two_sided
    assert first.p_one_sided == first.p_two_sided
