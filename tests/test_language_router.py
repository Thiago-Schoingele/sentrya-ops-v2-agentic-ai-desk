import unittest

from src.language_router import (
    build_language_instruction,
    detect_user_language,
    localize_public_response,
)


class TestLanguageRouter(unittest.TestCase):
    def test_01_detects_portuguese_with_accents(self):
        text = "Quero automatizar meu atendimento com IA e integrar com CRM."
        self.assertEqual(detect_user_language(text), "pt")

    def test_02_detects_english(self):
        text = "I want to automate my customer support and integrate it with my CRM."
        self.assertEqual(detect_user_language(text), "en")

    def test_03_empty_text_defaults_to_portuguese(self):
        self.assertEqual(detect_user_language(""), "pt")

    def test_04_builds_english_instruction(self):
        instruction = build_language_instruction("en")
        self.assertIn("You must answer in English only", instruction)

    def test_05_localizes_security_block_to_portuguese(self):
        response = {
            "intent": "security_block",
            "recommended_action": "Review the request manually before processing.",
            "summary": "The request was blocked by security validation.",
            "final_response": "I cannot process this request because it triggered the system security rules.",
        }

        localized = localize_public_response(response, "pt")

        self.assertEqual(localized["detected_language"], "pt")
        self.assertIn("Não posso processar", localized["final_response"])
        self.assertIn("validação de segurança", localized["summary"])

    def test_06_keeps_english_security_response_in_english(self):
        response = {
            "intent": "security_block",
            "recommended_action": "Review the request manually before processing.",
            "summary": "The request was blocked by security validation.",
            "final_response": "I cannot process this request because it triggered the system security rules.",
        }

        localized = localize_public_response(response, "en")

        self.assertEqual(localized["detected_language"], "en")
        self.assertIn("I cannot process", localized["final_response"])

    def test_07_localizes_lockdown_response_to_portuguese(self):
        response = {
            "intent": "system_lockdown",
            "recommended_action": "Operator review required before processing new operational requests.",
            "summary": "Sentrya Ops V2 is currently in security lockdown.",
            "final_response": "Sentrya Ops V2 is currently in security lockdown.",
        }

        localized = localize_public_response(response, "pt")

        self.assertEqual(localized["detected_language"], "pt")
        self.assertIn("bloqueio de segurança", localized["summary"])
        self.assertIn("solicitações operacionais", localized["final_response"])


if __name__ == "__main__":
    unittest.main()