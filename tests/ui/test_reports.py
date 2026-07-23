import pytest

from src.pages.pim.reports_page import ReportsPage
from src.data.factories import build_report_name


@pytest.mark.ui
@pytest.mark.smoke
def test_create_report(authenticated_page, base_url):
    report = build_report_name()

    reports_page = ReportsPage(
        authenticated_page,
        base_url
    ).open()

    (
        reports_page
        .open_add_report()
        .expect_form_loaded()

        # Report name
        .fill_report_name(report.report_name)


        .fill_selection_criteria("Employee Name")
        .add_selection_criteria()


        .expect_employee_field_visible()
        .fill_employee_name("test")

        # Include
        .fill_include("Current Employees Only")

        # Display Fields
        .fill_display_field_group("Personal")
        .fill_display_field("Employee Id")
        .add_display_field()

        # Save
        .save()
    )
    reports_page = ReportsPage(authenticated_page, base_url).open()
    assert reports_page.check_report_present(report.report_name), \
        (
        f"Expected created report '{report.report_name}' "
        "to appear in reports list"
    )


@pytest.mark.ui
@pytest.mark.smoke
def test_create_and_delete_report(authenticated_page, base_url):
    report = build_report_name()

    reports_page = ReportsPage(
        authenticated_page,
        base_url
    ).open()

    (
        reports_page
        .open_add_report()
        .expect_form_loaded()
        .fill_report_name(report.report_name)
        .fill_selection_criteria("Employee Name")
        .add_selection_criteria()
        .expect_employee_field_visible()
        .fill_employee_name("test")
        .fill_include("Current Employees Only")
        .fill_display_field_group("Personal")
        .fill_display_field("Employee Id")
        .add_display_field()
        .save()
    )

    reports_page = ReportsPage(
        authenticated_page,
        base_url
    ).open()
    assert reports_page.check_report_present(
        report.report_name
    )
    reports_page.select_report(
        report.report_name
    )
    reports_page.delete_selected_report()
    reports_page.accept_delete_modal()
    reports_page.wait_deleted_report_disappears(
        report.report_name
    )


@pytest.mark.ui
@pytest.mark.regression
def test_cancel_report_deletion(authenticated_page, base_url):
    report = build_report_name()

    reports_page = ReportsPage(
        authenticated_page,
        base_url
    ).open()
    (
        reports_page
        .open_add_report()
        .expect_form_loaded()
        .fill_report_name(report.report_name)
        .fill_selection_criteria("Employee Name")
        .add_selection_criteria()
        .expect_employee_field_visible()
        .fill_employee_name("test")
        .fill_include("Current Employees Only")
        .fill_display_field_group("Personal")
        .fill_display_field("Employee Id")
        .add_display_field()
        .save()
    )
    reports_page = ReportsPage(
        authenticated_page,
        base_url
    ).open()
    assert reports_page.check_report_present(
        report.report_name
    )
    reports_page.select_report(
        report.report_name
    )
    reports_page.delete_selected_report()
    reports_page.cancel_delete_modal()
    assert reports_page.check_report_present(
        report.report_name
    )
    reports_page.delete_selected_report()
    reports_page.accept_delete_modal()
    reports_page.wait_deleted_report_disappears(
        report.report_name
    )



@pytest.mark.ui
@pytest.mark.regression
def test_search_by_existing_report_returns_matching_row(authenticated_page,
                                                        base_url,
                                                        reports_test_data):
    report_name = reports_test_data["reports"]["existing"]
    reports_page = ReportsPage(authenticated_page, base_url).open()
    reports_page.search_report(report_name)
    assert reports_page.check_report_present(report_name), (
        f"Expected '{report_name}' to appear in results after search"
    )
    assert reports_page.get_records_count() >= 1


@pytest.mark.ui
@pytest.mark.regression
def test_search_results_are_filtered_to_the_searched_report(authenticated_page,
                                                            base_url,
                                                            reports_test_data):
    report_name = reports_test_data["reports"]["existing"]
    reports_page = ReportsPage(authenticated_page, base_url).open()
    full_count = reports_page.get_records_count()
    reports_page.search_report(report_name)
    filtered_count = reports_page.get_records_count()
    assert filtered_count <= full_count
    assert reports_page.check_report_present(report_name)



@pytest.mark.ui
@pytest.mark.regression
def test_autocomplete_suggests_matching_report_names(authenticated_page,
                                                     base_url,
                                                     reports_test_data):
    report_name = reports_test_data["reports"]["existing"]
    query = report_name[:5]
    reports_page = ReportsPage(authenticated_page, base_url).open()
    reports_page.report_name_input.fill(query)
    suggestions = reports_page.get_autocomplete_suggestions()
    assert suggestions, "Expected at least one autocomplete suggestion"
    assert all(query.lower() in s.lower() for s in suggestions), (
        f"Expected every suggestion to match query '{query}', got: {suggestions}"
    )



@pytest.mark.ui
@pytest.mark.regression
def test_reset_restores_full_report_list(authenticated_page,
                                         base_url,
                                         reports_test_data):
    report_name = reports_test_data["reports"]["existing"]
    reports_page = ReportsPage(authenticated_page, base_url).open()
    full_count = reports_page.get_records_count()
    reports_page.search_report(report_name)
    assert reports_page.get_records_count() <= full_count
    reports_page.reset_report()
    assert reports_page.get_records_count() == full_count
    assert reports_page.report_name_input.input_value() == ""



@pytest.mark.ui
@pytest.mark.regression
def test_search_for_non_existent_report_shows_no_results(authenticated_page,
                                                         base_url,
                                                         reports_test_data):
    report_name = reports_test_data["reports"]["non_existent"]
    reports_page = ReportsPage(authenticated_page, base_url).open()
    reports_page.report_name_input.fill(report_name)
    reports_page.search_btn.click()
    assert not reports_page.expect_report_absent(report_name)