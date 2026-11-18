package com.example.myapplication.activity;

import android.content.Intent;
import android.database.sqlite.SQLiteException;
import android.os.Bundle;
import android.view.View;

import com.example.myapplication.R;
import com.example.myapplication.database.DatabaseHelper;
import com.example.myapplication.databinding.ActivityLoginBinding;

public class LoginActivity extends AppointmentActivity {
    private ActivityLoginBinding binding;
    private DatabaseHelper database;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityLoginBinding.inflate(getLayoutInflater());
        setScreen(binding.getRoot());
        database = new DatabaseHelper(this);
        binding.btnLogin.setOnClickListener(view -> login());
    }

    private void login() {
        binding.tvError.setVisibility(View.GONE);
        String username = binding.etUsername.getText().toString().trim();
        String password = binding.etPassword.getText().toString();
        binding.etUsername.setError(username.isEmpty() ? getString(R.string.required_username) : null);
        binding.etPassword.setError(password.trim().isEmpty() ? getString(R.string.required_password) : null);
        if (username.isEmpty() || password.trim().isEmpty()) {
            return;
        }
        try {
            if (database.checkLogin(username, password)) {
                startActivity(new Intent(this, MainActivity.class));
                finish();
            } else {
                showError(R.string.login_error);
            }
        } catch (SQLiteException exception) {
            showError(R.string.database_error);
        }
    }

    private void showError(int message) {
        binding.tvError.setText(message);
        binding.tvError.setVisibility(View.VISIBLE);
    }

    @Override
    protected void onDestroy() {
        database.close();
        super.onDestroy();
    }
}
