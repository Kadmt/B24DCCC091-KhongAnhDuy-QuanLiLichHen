package com.example.myapplication.database;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.DatabaseUtils;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import com.example.myapplication.model.Appointment;

import java.util.ArrayList;

public class DatabaseHelper extends SQLiteOpenHelper {
    public static final String DB_NAME = "appointments.db";
    public static final int DB_VERSION = 1;
    public static final String TABLE_USERS = "users";
    public static final String TABLE_APPOINTMENTS = "appointments";

    public DatabaseHelper(Context context) {
        this(context, DB_NAME);
    }

    // Tests use their own file and never clear the application database.
    DatabaseHelper(Context context, String name) {
        super(context.getApplicationContext(), name, null, DB_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                + "username TEXT NOT NULL UNIQUE, password TEXT NOT NULL)");
        db.execSQL("CREATE TABLE appointments (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                + "title TEXT NOT NULL, location TEXT NOT NULL, date TEXT NOT NULL, "
                + "time TEXT NOT NULL, reminder INTEGER NOT NULL CHECK (reminder IN (0, 1)))");
        ContentValues user = new ContentValues();
        user.put("username", "admin");
        user.put("password", "123456");
        db.insertOrThrow(TABLE_USERS, null, user);
        db.insertOrThrow(TABLE_APPOINTMENTS, null, valuesOf(new Appointment(
                "Họp nhóm đồ án", "Phòng B203", "2026-10-25", "09:00", true)));
        db.insertOrThrow(TABLE_APPOINTMENTS, null, valuesOf(new Appointment(
                "Khám răng", "Nha khoa Minh Tâm", "2026-10-26", "14:30", true)));
        db.insertOrThrow(TABLE_APPOINTMENTS, null, valuesOf(new Appointment(
                "Đi cà phê với bạn", "Highland Coffee", "2026-10-27", "19:00", false)));
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        // Reset schema as specified by the version-1 assignment.
        db.execSQL("DROP TABLE IF EXISTS appointments");
        db.execSQL("DROP TABLE IF EXISTS users");
        onCreate(db);
    }

    public boolean checkLogin(String username, String password) {
        try (Cursor cursor = getReadableDatabase().query(TABLE_USERS, new String[]{"id"},
                "username = ? AND password = ?", new String[]{username, password},
                null, null, null, "1")) {
            return cursor.moveToFirst();
        }
    }

    public void insertUser(String username, String password) {
        ContentValues values = new ContentValues();
        values.put("username", username);
        values.put("password", password);
        getWritableDatabase().insertOrThrow(TABLE_USERS, null, values);
    }

    public long insertAppointment(Appointment appointment) {
        return getWritableDatabase().insertOrThrow(TABLE_APPOINTMENTS, null, valuesOf(appointment));
    }

    public ArrayList<Appointment> getAllAppointments() {
        ArrayList<Appointment> result = new ArrayList<>();
        try (Cursor cursor = getReadableDatabase().query(TABLE_APPOINTMENTS, null,
                null, null, null, null, "date ASC, time ASC, id ASC")) {
            while (cursor.moveToNext()) {
                result.add(readAppointment(cursor));
            }
        }
        return result;
    }

    public Appointment getAppointmentById(int id) {
        try (Cursor cursor = getReadableDatabase().query(TABLE_APPOINTMENTS, null,
                "id = ?", new String[]{String.valueOf(id)}, null, null, null)) {
            return cursor.moveToFirst() ? readAppointment(cursor) : null;
        }
    }

    public void updateReminder(int id, boolean on) {
        ContentValues values = new ContentValues();
        values.put("reminder", on ? 1 : 0);
        getWritableDatabase().update(TABLE_APPOINTMENTS, values, "id = ?",
                new String[]{String.valueOf(id)});
    }

    public void deleteAppointment(int id) {
        getWritableDatabase().delete(TABLE_APPOINTMENTS, "id = ?", new String[]{String.valueOf(id)});
    }

    public int countAll() {
        return (int) DatabaseUtils.longForQuery(getReadableDatabase(),
                "SELECT COUNT(*) FROM appointments", null);
    }

    public int countReminders() {
        return (int) DatabaseUtils.longForQuery(getReadableDatabase(),
                "SELECT COUNT(*) FROM appointments WHERE reminder = ?", new String[]{"1"});
    }

    private static ContentValues valuesOf(Appointment appointment) {
        ContentValues values = new ContentValues();
        values.put("title", appointment.getTitle());
        values.put("location", appointment.getLocation());
        values.put("date", appointment.getDate());
        values.put("time", appointment.getTime());
        values.put("reminder", appointment.isReminder() ? 1 : 0);
        return values;
    }

    private static Appointment readAppointment(Cursor cursor) {
        return new Appointment(cursor.getInt(cursor.getColumnIndexOrThrow("id")),
                cursor.getString(cursor.getColumnIndexOrThrow("title")),
                cursor.getString(cursor.getColumnIndexOrThrow("location")),
                cursor.getString(cursor.getColumnIndexOrThrow("date")),
                cursor.getString(cursor.getColumnIndexOrThrow("time")),
                cursor.getInt(cursor.getColumnIndexOrThrow("reminder")) == 1);
    }
}
