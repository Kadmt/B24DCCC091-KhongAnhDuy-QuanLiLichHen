package com.example.myapplication.activity;

import android.database.sqlite.SQLiteException;
import android.os.Bundle;
import android.widget.Toast;

import com.example.myapplication.R;
import com.example.myapplication.database.DatabaseHelper;
import com.example.myapplication.databinding.ActivityAddAppointmentBinding;
import com.example.myapplication.model.Appointment;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Locale;

public class AddAppointmentActivity extends AppointmentActivity {
    private ActivityAddAppointmentBinding binding;
    private DatabaseHelper database;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityAddAppointmentBinding.inflate(getLayoutInflater());
        setScreen(binding.getRoot());
        database = new DatabaseHelper(this);
        binding.tpTime.setIs24HourView(true);
        if (savedInstanceState == null) {
            Calendar nextHour = Calendar.getInstance();
            nextHour.add(Calendar.HOUR_OF_DAY, 1);
            binding.dpDate.updateDate(nextHour.get(Calendar.YEAR), nextHour.get(Calendar.MONTH),
                    nextHour.get(Calendar.DAY_OF_MONTH));
            binding.tpTime.setHour(nextHour.get(Calendar.HOUR_OF_DAY));
            binding.tpTime.setMinute(nextHour.get(Calendar.MINUTE));
        }
        binding.btnBack.setOnClickListener(view -> finish());
        binding.btnSave.setOnClickListener(view -> save());
    }

    private void save() {
        // Commit any number currently being edited in a spinner before reading it.
        binding.dpDate.clearFocus();
        binding.tpTime.clearFocus();
        String title = binding.etTitle.getText().toString().trim();
        String location = binding.etLocation.getText().toString().trim();
        binding.etTitle.setError(title.isEmpty() ? getString(R.string.required_title) : null);
        binding.etLocation.setError(location.isEmpty() ? getString(R.string.required_location) : null);
        if (title.isEmpty() || location.isEmpty()) {
            return;
        }
        Calendar selected = Calendar.getInstance();
        selected.clear();
        selected.set(binding.dpDate.getYear(), binding.dpDate.getMonth(),
                binding.dpDate.getDayOfMonth(), binding.tpTime.getHour(), binding.tpTime.getMinute());
        if (!selected.after(Calendar.getInstance())) {
            Toast.makeText(this, R.string.future_time_required, Toast.LENGTH_LONG).show();
            return;
        }
        Appointment appointment = new Appointment(title, location,
                new SimpleDateFormat("yyyy-MM-dd", Locale.ROOT).format(selected.getTime()),
                new SimpleDateFormat("HH:mm", Locale.ROOT).format(selected.getTime()),
                binding.swReminder.isChecked());
        try {
            database.insertAppointment(appointment);
            Toast.makeText(this, R.string.add_success, Toast.LENGTH_SHORT).show();
            finish();
        } catch (SQLiteException exception) {
            Toast.makeText(this, R.string.database_error, Toast.LENGTH_LONG).show();
        }
    }

    @Override
    protected void onDestroy() {
        database.close();
        super.onDestroy();
    }
}
