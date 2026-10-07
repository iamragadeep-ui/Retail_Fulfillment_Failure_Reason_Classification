import json

from backend.app.observability.database import get_connection


DEMO_METADATA = json.dumps(
    {
        "source": "demo_seed",
        "demo": True,
        "project": "Retail Fulfillment Failure Reason Classification",
    }
)


def seed_demo_data():
    connection = get_connection()

    try:
        # Prevent duplicate demo seed data.
        existing = connection.execute(
            """
            SELECT COUNT(*)
            FROM model_drift
            WHERE metadata LIKE '%demo_seed%'
            """
        ).fetchone()[0]

        if existing:
            print("Demo observability data already exists. Skipping seed.")
            return

        connection.execute(
            """
            INSERT INTO model_drift (
                metric_name,
                baseline_value,
                current_value,
                drift_score,
                status,
                environment,
                metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "classification_confidence",
                0.92,
                0.88,
                0.04,
                "STABLE",
                "demo",
                DEMO_METADATA,
            ),
        )

        connection.execute(
            """
            INSERT INTO data_drift (
                feature_name,
                psi,
                ks_statistic,
                js_divergence,
                wasserstein_distance,
                status,
                environment,
                metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "failure_description_length",
                0.08,
                0.07,
                0.04,
                0.05,
                "STABLE",
                "demo",
                DEMO_METADATA,
            ),
        )

        connection.execute(
            """
            INSERT INTO prediction_drift (
                prediction_type,
                baseline_distribution,
                current_distribution,
                drift_score,
                status,
                environment,
                metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "failure_reason",
                json.dumps(
                    {
                        "CARRIER_DELAY": 0.40,
                        "INVENTORY": 0.30,
                        "PAYMENT": 0.20,
                        "OTHER": 0.10,
                    }
                ),
                json.dumps(
                    {
                        "CARRIER_DELAY": 0.44,
                        "INVENTORY": 0.28,
                        "PAYMENT": 0.18,
                        "OTHER": 0.10,
                    }
                ),
                0.04,
                "STABLE",
                "demo",
                DEMO_METADATA,
            ),
        )

        connection.execute(
            """
            INSERT INTO concept_drift (
                accuracy,
                precision_score,
                recall_score,
                f1_score,
                roc_auc,
                baseline_score,
                current_score,
                drift_score,
                status,
                environment,
                metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                0.91,
                0.90,
                0.89,
                0.895,
                0.93,
                0.92,
                0.895,
                0.025,
                "STABLE",
                "demo",
                DEMO_METADATA,
            ),
        )

        connection.execute(
            """
            INSERT INTO prompt_drift (
                prompt_length,
                prompt_tokens,
                system_prompt_version,
                prompt_template_version,
                instruction_changes,
                embedding_similarity,
                prompt_failure_rate,
                drift_score,
                status,
                environment,
                metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                420,
                105,
                "v1.0",
                "v1.0",
                "No material instruction change",
                0.97,
                0.01,
                0.03,
                "STABLE",
                "demo",
                DEMO_METADATA,
            ),
        )

        connection.execute(
            """
            INSERT INTO retrieval_drift (
                average_similarity_score,
                documents_retrieved,
                document_distribution,
                top_k,
                context_tokens,
                retrieval_latency_ms,
                no_result_rate,
                precision_at_k,
                recall_at_k,
                mrr,
                ndcg,
                drift_score,
                status,
                environment,
                metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                0.86,
                5,
                json.dumps(
                    {
                        "policy": 2,
                        "carrier": 2,
                        "inventory": 1,
                    }
                ),
                5,
                650,
                42.5,
                0.02,
                0.88,
                0.84,
                0.91,
                0.89,
                0.04,
                "STABLE",
                "demo",
                DEMO_METADATA,
            ),
        )

        connection.execute(
            """
            INSERT INTO output_drift (
                response_length,
                response_tokens,
                sentiment,
                classification,
                refusal_rate,
                hallucination_rate,
                groundedness,
                faithfulness,
                drift_score,
                status,
                environment,
                metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                620,
                150,
                "neutral",
                "CARRIER_DELAY",
                0.01,
                0.02,
                0.94,
                0.95,
                0.03,
                "STABLE",
                "demo",
                DEMO_METADATA,
            ),
        )

        connection.commit()

        print("Demo observability seed data inserted successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    seed_demo_data()