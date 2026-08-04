CREATE TRIGGER IF NOT EXISTS procurement_cases_status_insert_contract
BEFORE INSERT ON procurement_cases
WHEN NEW.status NOT IN (
    'WATCHING', 'QUALIFYING', 'READY_FOR_REVIEW',
    'BUY_CANDIDATE', 'PURCHASED', 'CANCELLED'
)
BEGIN
    SELECT RAISE(ABORT, 'invalid procurement lifecycle status');
END;

CREATE TRIGGER IF NOT EXISTS procurement_cases_status_update_contract
BEFORE UPDATE OF status ON procurement_cases
WHEN NEW.status NOT IN (
    'WATCHING', 'QUALIFYING', 'READY_FOR_REVIEW',
    'BUY_CANDIDATE', 'PURCHASED', 'CANCELLED'
)
BEGIN
    SELECT RAISE(ABORT, 'invalid procurement lifecycle status');
END;

CREATE TRIGGER IF NOT EXISTS procurement_cases_transition_update_contract
BEFORE UPDATE OF status ON procurement_cases
WHEN OLD.status <> NEW.status AND NOT (
    (OLD.status = 'WATCHING' AND NEW.status IN ('QUALIFYING', 'CANCELLED')) OR
    (OLD.status = 'QUALIFYING' AND NEW.status IN ('READY_FOR_REVIEW', 'CANCELLED')) OR
    (OLD.status = 'READY_FOR_REVIEW' AND NEW.status IN ('BUY_CANDIDATE', 'CANCELLED')) OR
    (OLD.status = 'BUY_CANDIDATE' AND NEW.status IN ('PURCHASED', 'CANCELLED'))
)
BEGIN
    SELECT RAISE(ABORT, 'invalid procurement lifecycle transition');
END;
