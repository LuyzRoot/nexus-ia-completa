from plugins.skills.calculator import CalculatorSkill

def test_calculator():
    skill = CalculatorSkill()
    res = skill.run({"expression": "1+2"})
    assert res.get("result") == 3
