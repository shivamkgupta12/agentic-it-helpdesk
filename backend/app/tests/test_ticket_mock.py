from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.database_models import User, UserRole
from app.services.ticket_service import TicketCreateInput, TicketService


def test_mock_ticket_creation() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    user = User(
        email="employee@example.com",
        name="employee",
        role=UserRole.employee,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    service = TicketService(db)

    ticket = service.create_ticket(
        TicketCreateInput(
            user_id=user.id,
            conversation_id=None,
            title="VPN connectivity issue",
            description="VPN keeps disconnecting.",
            category="Network / VPN",
            priority="Medium",
            urgency="Medium",
        )
    )

    assert ticket.ticket_number is not None
    assert ticket.ticket_number.startswith("MOCK")
    assert ticket.status.value == "open"
    assert ticket.source == "mock"

    db.close()