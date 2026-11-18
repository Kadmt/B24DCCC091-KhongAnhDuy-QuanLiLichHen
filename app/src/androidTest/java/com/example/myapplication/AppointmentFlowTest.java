package com.example.myapplication;

import static androidx.test.espresso.Espresso.onData;
import static androidx.test.espresso.Espresso.onView;
import static androidx.test.espresso.action.ViewActions.*;
import static androidx.test.espresso.assertion.ViewAssertions.matches;
import static androidx.test.espresso.matcher.ViewMatchers.*;
import static org.junit.Assert.*;

import android.app.Activity;
import android.content.Context;
import android.widget.DatePicker;
import android.widget.TimePicker;
import androidx.test.core.app.ActivityScenario;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.runner.lifecycle.ActivityLifecycleMonitorRegistry;
import androidx.test.runner.lifecycle.Stage;
import com.example.myapplication.activity.AddAppointmentActivity;
import com.example.myapplication.activity.LoginActivity;
import com.example.myapplication.database.DatabaseHelper;
import com.example.myapplication.model.Appointment;
import org.hamcrest.Description;
import org.hamcrest.TypeSafeMatcher;
import org.junit.Test;
import org.junit.runner.RunWith;
import java.util.Calendar;
import java.util.concurrent.atomic.AtomicReference;

@RunWith(AndroidJUnit4.class)
public class AppointmentFlowTest {
    @Test public void addRejectsEmptyFieldsAndPastTime() {
        Context context = InstrumentationRegistry.getInstrumentation().getTargetContext();
        try (DatabaseHelper database = new DatabaseHelper(context);
             ActivityScenario<AddAppointmentActivity> scenario = ActivityScenario.launch(AddAppointmentActivity.class)) {
            int total = database.countAll();
            onView(withId(R.id.btnSave)).perform(scrollTo(), click());
            scenario.onActivity(activity -> {
                assertNotNull(((android.widget.EditText) activity.findViewById(R.id.etTitle)).getError());
                assertNotNull(((android.widget.EditText) activity.findViewById(R.id.etLocation)).getError());
            });
            onView(withId(R.id.etTitle)).perform(scrollTo(), replaceText("Lịch trong quá khứ"));
            onView(withId(R.id.etLocation)).perform(scrollTo(), replaceText("A"), closeSoftKeyboard());
            scenario.onActivity(activity -> {
                Calendar yesterday = Calendar.getInstance();
                yesterday.add(Calendar.DAY_OF_MONTH, -1);
                ((DatePicker) activity.findViewById(R.id.dpDate)).updateDate(yesterday.get(Calendar.YEAR),
                        yesterday.get(Calendar.MONTH), yesterday.get(Calendar.DAY_OF_MONTH));
            });
            onView(withId(R.id.btnSave)).perform(scrollTo(), click());
            assertEquals(total, database.countAll());
            scenario.onActivity(activity -> assertFalse(activity.isFinishing()));
        }
    }

    @Test public void loginValidatesEmptyAndIncorrectCredentials() {
        try (ActivityScenario<LoginActivity> scenario = ActivityScenario.launch(LoginActivity.class)) {
            onView(withId(R.id.btnLogin)).perform(click());
            onView(withId(R.id.etUsername)).check(matches(hasErrorText("Vui lòng nhập tên đăng nhập")));
            onView(withId(R.id.etPassword)).check(matches(hasErrorText("Vui lòng nhập mật khẩu")));
            onView(withId(R.id.etUsername)).perform(replaceText("admin"));
            onView(withId(R.id.etPassword)).perform(replaceText("wrong"), closeSoftKeyboard());
            onView(withId(R.id.btnLogin)).perform(click());
            onView(withId(R.id.tvError)).check(matches(isDisplayed()));
            onView(withId(R.id.tvError)).check(matches(withText(R.string.login_error)));
        }
    }

    @Test public void addToggleDelete_refreshesStatsAndLoginFinishes() {
        Context context = InstrumentationRegistry.getInstrumentation().getTargetContext();
        String title = "UI test " + System.nanoTime();
        try (DatabaseHelper database = new DatabaseHelper(context);
             ActivityScenario<LoginActivity> scenario = ActivityScenario.launch(LoginActivity.class)) {
            int total = database.countAll();
            int reminders = database.countReminders();
            AtomicReference<LoginActivity> login = new AtomicReference<>();
            scenario.onActivity(login::set);
            onView(withId(R.id.etUsername)).perform(replaceText("admin"));
            onView(withId(R.id.etPassword)).perform(replaceText("123456"), closeSoftKeyboard());
            onView(withId(R.id.btnLogin)).perform(click());
            onView(withId(R.id.btnAdd)).check(matches(isDisplayed()));
            assertTrue(login.get().isFinishing() || login.get().isDestroyed());
            onView(withId(R.id.btnAdd)).perform(click());
            onView(withId(R.id.etTitle)).perform(replaceText(title));
            onView(withId(R.id.etLocation)).perform(replaceText("Phòng kiểm thử"), closeSoftKeyboard());
            InstrumentationRegistry.getInstrumentation().runOnMainSync(() -> {
                Activity activity = resumedActivity();
                assertTrue(activity instanceof AddAppointmentActivity);
                Calendar tomorrow = Calendar.getInstance();
                tomorrow.add(Calendar.DAY_OF_MONTH, 1);
                ((DatePicker) activity.findViewById(R.id.dpDate)).updateDate(tomorrow.get(Calendar.YEAR),
                        tomorrow.get(Calendar.MONTH), tomorrow.get(Calendar.DAY_OF_MONTH));
                TimePicker time = activity.findViewById(R.id.tpTime);
                time.setHour(10);
                time.setMinute(30);
            });
            onView(withId(R.id.btnSave)).perform(scrollTo(), click());
            onView(withId(R.id.tvStats)).check(matches(withText(context.getString(R.string.stats_format, total + 1, reminders + 1))));
            openAppointment(title);
            onView(withId(R.id.tvReminderStatus)).check(matches(withText(R.string.reminder_on)));
            onView(withId(R.id.swReminder)).perform(scrollTo(), click());
            onView(withId(R.id.tvReminderStatus)).check(matches(withText(R.string.reminder_off)));
            onView(withId(R.id.btnBack)).perform(scrollTo(), click());
            onView(withId(R.id.tvStats)).check(matches(withText(context.getString(R.string.stats_format, total + 1, reminders))));
            openAppointment(title);
            onView(withId(R.id.tvReminderStatus)).check(matches(withText(R.string.reminder_off)));
            onView(withId(R.id.btnDelete)).perform(scrollTo(), click());
            onView(withText(R.string.delete)).perform(click());
            onView(withId(R.id.tvStats)).check(matches(withText(context.getString(R.string.stats_format, total, reminders))));
        } finally {
            InstrumentationRegistry.getInstrumentation().runOnMainSync(() -> {
                Activity current = resumedActivity();
                if (current != null) current.finish();
            });
            try (DatabaseHelper database = new DatabaseHelper(context)) {
                for (Appointment appointment : database.getAllAppointments()) {
                    if (title.equals(appointment.getTitle())) database.deleteAppointment(appointment.getId());
                }
            }
        }
    }

    private static Activity resumedActivity() {
        for (Activity activity : ActivityLifecycleMonitorRegistry.getInstance().getActivitiesInStage(Stage.RESUMED)) {
            return activity;
        }
        return null;
    }

    private static void openAppointment(String title) {
        onData(new TypeSafeMatcher<Appointment>() {
            @Override protected boolean matchesSafely(Appointment item) { return title.equals(item.getTitle()); }
            @Override public void describeTo(Description description) { description.appendText(title); }
        }).inAdapterView(withId(R.id.lvAppointments)).perform(click());
    }
}
