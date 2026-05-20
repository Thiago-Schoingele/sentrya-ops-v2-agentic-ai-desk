import unittest

from src.llm_roles import (
    LLM_ROLE_REGISTRY,
    detect_capability_answer_language,
    format_capability_answer,
    format_llm_roles_for_telegram,
    get_llm_role,
    get_llm_roles,
    is_llm_capability_question,
)


class LlmRolesTestCase(unittest.TestCase):
    def test_registry_has_exactly_four_roles(self):
        self.assertEqual(len(get_llm_roles()), 4)

    def test_expected_role_ids_exist(self):
        self.assertEqual(set(LLM_ROLE_REGISTRY), {"fast", "agent", "reasoning", "general"})

    def test_each_role_has_required_operational_fields(self):
        for role in get_llm_roles().values():
            self.assertTrue(role.model_name)
            self.assertTrue(role.primary_function)
            self.assertTrue(role.scope_guardrail)

    def test_each_role_is_restricted_to_sentrya_ops_v2(self):
        for role in get_llm_roles().values():
            combined_text = " ".join(
                [
                    role.primary_function,
                    role.use_when,
                    role.must_not_do,
                    role.scope_guardrail,
                ]
            )
            self.assertIn("Sentrya Ops V2", combined_text)
            self.assertIn("only inside the Sentrya Ops V2", role.scope_guardrail)

    def test_unknown_role_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_llm_role("unknown")

    def test_telegram_formatting_contains_all_four_models(self):
        text = format_llm_roles_for_telegram()

        self.assertIn("llama-3.1-8b-instant", text)
        self.assertIn("openai/gpt-oss-20b", text)
        self.assertIn("openai/gpt-oss-120b", text)
        self.assertIn("llama-3.3-70b-versatile", text)

    def test_portuguese_capability_questions_are_detected(self):
        self.assertTrue(is_llm_capability_question("Qual a sua habilidade?"))
        self.assertTrue(is_llm_capability_question("Quais são suas habilidades?"))
        self.assertTrue(is_llm_capability_question("O que você sabe fazer?"))

    def test_english_capability_questions_are_detected(self):
        self.assertTrue(is_llm_capability_question("What can you do?"))
        self.assertTrue(is_llm_capability_question("What are your capabilities?"))

    def test_capability_answer_is_limited_to_sentrya_ops_v2_scope(self):
        portuguese_answer = format_capability_answer("pt")
        english_answer = format_capability_answer("en")

        self.assertIn("escopo operacional do Sentrya Ops V2", portuguese_answer)
        self.assertIn("limited to the operational scope of Sentrya Ops V2", english_answer)
        self.assertIn("Scope rule", english_answer)
        self.assertIn("Sentrya Ops V2", portuguese_answer)

    def test_capability_answer_language_detects_clear_english_questions(self):
        self.assertEqual(detect_capability_answer_language("What can you do?", "pt"), "en")
        self.assertEqual(detect_capability_answer_language("What are your capabilities?", "pt"), "en")
        self.assertEqual(detect_capability_answer_language("What are your skills?", "pt"), "en")

    def test_capability_answer_language_detects_clear_portuguese_questions(self):
        self.assertEqual(detect_capability_answer_language("Qual a sua habilidade?", "en"), "pt")
        self.assertEqual(detect_capability_answer_language("Qual sua função?", "en"), "pt")

    def test_english_capability_answer_is_fully_english(self):
        answer = format_capability_answer("en")

        self.assertIn("My capabilities", answer)
        self.assertNotIn("Minhas habilidades", answer)

    def test_portuguese_capability_answer_is_fully_portuguese(self):
        answer = format_capability_answer("pt")

        self.assertIn("Minhas habilidades", answer)
        self.assertNotIn("My capabilities", answer)


if __name__ == "__main__":
    unittest.main()
